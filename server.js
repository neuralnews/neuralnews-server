var request       = require('request');
var app           = require('express')();
var http          = require('http').Server(app);
var https         = require('https');
var path          = require('path');
var express       = require('express');
var bodyParser    = require('body-parser');
var validator     = require('validator');
var fetch         = require('node-fetch');
var AYLIENTextAPI = require('aylien_textapi');
var textapi       = new AYLIENTextAPI({
        application_id: "a5ad45d9",
        application_key: "2c891b3f58381a7842d500c5fb534b8e"
});
var PythonShell   = require('python-shell');
var utf8          = require('utf8');
var Q             = require('q');

/*
var bigtable      = require('@google-cloud/bigtable')({ projectId: 'neural-news-185122' });
var instance = bigtable.instance('my-instance');
var table = instance.table('prezzy');*/

/* Setting app properties */
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(require('express').static(__dirname + '/public'));

/* Serve index page */
app.get('/', function (req, res) {
        res.sendFile(__dirname + '/index.html');
});

/* Serve test data */
app.get('/sanders.json', function(req, res) {
        res.sendFile(__dirname + '/test_data/sanders.json');
});
app.get('/trump.json', function(req, res) {
        res.sendFile(__dirname + '/test_data/trump.json');
});
app.get('/trump_raw.json', function(req, res) {
        //res.sendFile(__dirname + '/test_data/trump_raw.json');
        var articles = require('./test_data/trump_raw.json');
        var startDate = Date.now();
        new_process_articles(articles, startDate).then(function(data) {
          res.send(JSON.stringify(data));
        });
});

/* Serve trending topics */
app.get('/trendingtopics', function(req, res) {
        res.sendFile(__dirname + '/trendingtopics.json');
});

/* Trying out things from scratch... */
app.get('/query', function(req, res) {

        /* Microsoft Azure Cognitive Services */
        var subscription_key = 'bfc96e2d7cee4696b2e3bd85c2f4816c';
        var host             = 'api.cognitive.microsoft.com';
        var path             = '/bing/v7.0/news/search';
        var term             = req.query.search;
        var startDate        = Date.now();
        var request_params   = {
                method : 'GET',
                hostname : host,
                path : path + '?q=' + term,
                headers : {
                    'Ocp-Apim-Subscription-Key' : subscription_key,
                }
        };

        // Handles response
        var response_handler = function (response) {
            var body = "";
            response.on('data', function (d) {
                body += d;
            });
            response.on('end', function () {
                articles = JSON.parse(body).value;
                new_process_articles(articles, startDate).then(function(data) {
                        res.send(JSON.stringify(data));
                });
            });
            response.on('error', function (e) {
                console.log('Error: ' + e.message);
            });
        };

        var bing_news_search = function (search) {
          console.log('Searching news for: ' + search);
          var request_params = {
                method : 'GET',
                hostname : host,
                path : path + '?q=' + encodeURIComponent(search),
                headers : {
                    'Ocp-Apim-Subscription-Key' : subscription_key,
                }
            };

            var req = https.request(request_params, response_handler);
            req.end();
        }

        bing_news_search(term);
});

// Given object of articles, returns a JSON string with all the data
// needed by the app
function new_process_articles(articles, startDate)
{
        var deferred       = Q.defer();
        var result         = [];

        textapi.extract({
                url: articles[0].url,
                best_image: true
        }, function(error, response) {
                if (error) {
                        console.log("LOG: ERROR: " + JSON.stringify(error));
                        console.log("==> Result: " + JSON.stringify(response));
                } else {
                        console.log("* * Extracted text successfully");
                        console.log("Time to extract article text: " + ((Date.now() - startDate) / 1000).toString() + " seconds\n");

                        // 2a. TODO: sanitize text (remove quotes, etc.)
                        var article_text  = response.article;

                        // The path to your python script
                        var myPythonScript = "./scripts/nlp_v2.py";

                        // Provide the path of the python executable, if python is available as environment variable then you can use only "python"
                        var pythonExecutable = "python";

                        // Function to convert an Uint8Array to a string
                        var uint8arrayToString = function(data){
                            return String.fromCharCode.apply(null, data);
                        };

                        // Spawn child process
                        const spawn           = require("child_process").spawn;
                        const scriptExecution = spawn(pythonExecutable, [myPythonScript, article_text.replace(/[^\w.]+/g, " ")]);
                        scriptExecution.stdout.setEncoding('utf8');

                        stdout_1 = '';
                        // Handle normal output
                        scriptExecution.stdout.on('data', (data) => {
                                stdout_1 += data;
                        });

                        scriptExecution.stdout.on('end', () => {
                            data_obj = process_nlp_data(JSON.parse(stdout_1), startDate, response.title, articles[0].description, articles[0].image ? articles[0].image.thumbnail.contentUrl : 'null', articles[0].url, articles[0].provider[0].name)
                            result.push({
                                    "article" : data_obj
                            });
                            console.log("PUSHED SUCCESSFULLY, SIZE OF RESULTS: " + result.length.toString());
                            if (result.length == 5) {
                                    deferred.resolve(result);
                            }
                        });

                        // Handle error output
                        scriptExecution.stderr.on('data', (data) => {
                            console.log("ERROR: " + uint8arrayToString(data));
                        });
                }
        });

        textapi.extract({
                url: articles[1].url,
                best_image: true
        }, function(error, response) {
                if (error) {
                        console.log("LOG: ERROR: " + JSON.stringify(error));
                        console.log("==> Result: " + JSON.stringify(response));
                } else {
                        console.log("* * Extracted text successfully");
                        console.log("Time to extract article text: " + ((Date.now() - startDate) / 1000).toString() + " seconds\n");

                        // 2a. TODO: sanitize text (remove quotes, etc.)
                        var article_text  = response.article;

                        // The path to your python script
                        var myPythonScript = "./scripts/nlp_v2.py";

                        // Provide the path of the python executable, if python is available as environment variable then you can use only "python"
                        var pythonExecutable = "python";

                        // Function to convert an Uint8Array to a string
                        var uint8arrayToString = function(data){
                            return String.fromCharCode.apply(null, data);
                        };

                        // Spawn child process
                        const spawn           = require("child_process").spawn;
                        const scriptExecution = spawn(pythonExecutable, [myPythonScript, article_text.replace(/[^\w.]+/g, " ")]);
                        scriptExecution.stdout.setEncoding('utf8');

                        stdout_2 = '';
                        // Handle normal output
                        scriptExecution.stdout.on('data', (data) => {
                                stdout_2 += data;
                        });

                        scriptExecution.stdout.on('end', () => {
                            console.log("*** ==> Python script executed successfully!");
                            data_obj = process_nlp_data(JSON.parse(stdout_2), startDate, response.title, articles[1].description, articles[1].image ? articles[1].image.thumbnail.contentUrl : 'null', articles[1].url, articles[1].provider[0].name)
                            result.push({
                                    "article" : data_obj
                            });
                            console.log("PUSHED SUCCESSFULLY, SIZE OF RESULTS: " + result.length.toString());
                            if (result.length == 5) {
                                    deferred.resolve(result);
                            }
                        });

                        // Handle error output
                        scriptExecution.stderr.on('data', (data) => {
                            console.log("ERROR: " + uint8arrayToString(data));
                        });
                }
        });

        textapi.extract({
                url: articles[2].url,
                best_image: true
        }, function(error, response) {
                if (error) {
                        console.log("LOG: ERROR: " + JSON.stringify(error));
                        console.log("==> Result: " + JSON.stringify(response));
                } else {
                        console.log("* * Extracted text successfully");
                        console.log("Time to extract article text: " + ((Date.now() - startDate) / 1000).toString() + " seconds\n");

                        // 2a. TODO: sanitize text (remove quotes, etc.)
                        var article_text  = response.article;

                        // The path to your python script
                        var myPythonScript = "./scripts/nlp_v2.py";

                        // Provide the path of the python executable, if python is available as environment variable then you can use only "python"
                        var pythonExecutable = "python";

                        // Function to convert an Uint8Array to a string
                        var uint8arrayToString = function(data){
                            return String.fromCharCode.apply(null, data);
                        };

                        // Spawn child process
                        const spawn           = require("child_process").spawn;
                        const scriptExecution = spawn(pythonExecutable, [myPythonScript, article_text.replace(/[^\w.]+/g, " ")]);
                        scriptExecution.stdout.setEncoding('utf8');

                        stdout_3 = ''

                        // Handle normal output
                        scriptExecution.stdout.on('data', (data) => {
                                stdout_3 += data;
                        });

                        // Handle error output
                        scriptExecution.stderr.on('data', (data) => {
                            console.log("ERROR: " + uint8arrayToString(data));
                        });

                        scriptExecution.stdout.on('end', () => {
                            data_obj = process_nlp_data(JSON.parse(stdout_3), startDate, response.title, articles[2].description, articles[2].image ? articles[2].image.thumbnail.contentUrl : 'null', articles[2].url, articles[2].provider[0].name)
                            result.push({
                                    "article" : data_obj
                            });
                            console.log("PUSHED SUCCESSFULLY, SIZE OF RESULTS: " + result.length.toString());
                            if (result.length == 5) {
                                    deferred.resolve(result);
                            }
                        })
                }
        });

        textapi.extract({
                url: articles[3].url,
                best_image: true
        }, function(error, response) {
                if (error) {
                        console.log("LOG: ERROR: " + JSON.stringify(error));
                        console.log("==> Result: " + JSON.stringify(response));
                } else {
                        console.log("* * Extracted text successfully");
                        console.log("Time to extract article text: " + ((Date.now() - startDate) / 1000).toString() + " seconds\n");

                        // 2a. TODO: sanitize text (remove quotes, etc.)
                        var article_text  = response.article;

                        // The path to your python script
                        var myPythonScript = "./scripts/nlp_v2.py";

                        // Provide the path of the python executable, if python is available as environment variable then you can use only "python"
                        var pythonExecutable = "python";

                        // Function to convert an Uint8Array to a string
                        var uint8arrayToString = function(data){
                            return String.fromCharCode.apply(null, data);
                        };

                        // Spawn child process
                        const spawn           = require("child_process").spawn;
                        const scriptExecution = spawn(pythonExecutable, [myPythonScript, article_text.replace(/[^\w.]+/g, " ")]);
                        scriptExecution.stdout.setEncoding('utf8');

                        stdout_4 = ''

                        // Handle normal output
                        scriptExecution.stdout.on('data', (data) => {
                                stdout_4 += data;
                        });

                        // Handle error output
                        scriptExecution.stderr.on('data', (data) => {
                            console.log("ERROR: " + uint8arrayToString(data));
                        });

                        scriptExecution.stdout.on('end', () => {
                            data_obj = process_nlp_data(JSON.parse(stdout_4), startDate, response.title, articles[3].description, articles[3].image ? articles[3].image.thumbnail.contentUrl : 'null', articles[3].url, articles[3].provider[0].name)
                            result.push({
                                    "article" : data_obj
                            });
                            console.log("PUSHED SUCCESSFULLY, SIZE OF RESULTS: " + result.length.toString());
                            if (result.length == 5) {
                                    deferred.resolve(result);
                            }
                        })
                }
        });

        textapi.extract({
                url: articles[4].url,
                best_image: true
        }, function(error, response) {
                if (error) {
                        console.log("LOG: ERROR: " + JSON.stringify(error));
                        console.log("==> Result: " + JSON.stringify(response));
                } else {
                        console.log("* * Extracted text successfully");
                        console.log("Time to extract article text: " + ((Date.now() - startDate) / 1000).toString() + " seconds\n");

                        // 2a. TODO: sanitize text (remove quotes, etc.)
                        var article_text  = response.article;

                        // The path to your python script
                        var myPythonScript = "./scripts/nlp_v2.py";

                        // Provide the path of the python executable, if python is available as environment variable then you can use only "python"
                        var pythonExecutable = "python";

                        // Function to convert an Uint8Array to a string
                        var uint8arrayToString = function(data){
                            return String.fromCharCode.apply(null, data);
                        };

                        // Spawn child process
                        const spawn           = require("child_process").spawn;
                        const scriptExecution = spawn(pythonExecutable, [myPythonScript, article_text.replace(/[^\w.]+/g, " ")]);
                        scriptExecution.stdout.setEncoding('utf8');

                        stdout_5 = ''

                        // Handle normal output
                        scriptExecution.stdout.on('data', (data) => {
                                stdout_5 += data;
                        });

                        // Handle error output
                        scriptExecution.stderr.on('data', (data) => {
                            console.log("ERROR: " + uint8arrayToString(data));
                        });

                        scriptExecution.stdout.on('end', () => {
                            data_obj = process_nlp_data(JSON.parse(stdout_5), startDate, response.title, articles[4].description, articles[4].image ? articles[4].image.thumbnail.contentUrl : 'null', articles[4].url, articles[4].provider[0].name)
                            result.push({
                                    "article" : data_obj
                            });
                            console.log("PUSHED SUCCESSFULLY, SIZE OF RESULTS: " + result.length.toString());
                            if (result.length == 5) {
                                    deferred.resolve(result);
                            }
                        })
                }
        });

        return deferred.promise;
}

function toUnicode(theString) {
        var unicodeString = '';
        for (var i=0; i < theString.length; i++) {
                var theUnicode = theString.charCodeAt(i).toString(16).toUpperCase();
                while (theUnicode.length < 4) {
                        theUnicode = '0' + theUnicode;
                }
                theUnicode = '\\u' + theUnicode;
                unicodeString += theUnicode;
        }
        return unicodeString;
}

/*
 * process_nlp_data
 *
 */
function process_nlp_data(entities, startDate, article_title, description, thumbnail, url, news_source)
{
        var ents   = entities;
        var result = {
                data : [
                    ents[0],
                    ents[1],
                    ents[2],
                    ents[3],
                    ents[4],
                ],
                title       : article_title,
                description : description,
                source      : news_source,
                url         : url,
                thumbnail   : thumbnail
        };
        console.log("* * * * * Text processed => printing results...")
        console.log(result);
        console.log("Time to iterate over sentences looking for entities: " + ((Date.now() - startDate) / 1000).toString() + " seconds\n");

        return result;

}

/*
 * sanitizeText
 * Given a string, sanitizes and returns a version of the string without
 * dialogue quotes, etc.
 */
function sanitizeText(response)
{
        return response.article;
}

/*
 * santitizeSentences
 */
function sanitizeSentences(sentences)
{
        for (sentence in sentences) {
                sentences[sentence] = sentence.replace(/\/r/g, '');
        }
        return sentences;
}

/*
 * getEntities
 * Returns the top three
 */
function getEntities(response)
{
        // TODO: Make this work a little better...
        var ents = [];
        if (response.organization)
                ents.push(response.organization[0]);
        else
                ents.push(response.keyword[0]);
        if (response.location)
                ents.push(response.location[0]);
        else
                ents.push(response.keyword[1]);
        if (response.person)
                ents.push(response.person[0]);
        else
                ents.push(response.keyword[2]);
        return ents;
}

http.listen(process.env.PORT || 3000, function() {
        console.log('listening on port:3000');
});
