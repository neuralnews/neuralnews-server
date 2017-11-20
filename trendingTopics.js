import React, { Component } from 'react';
import {
    View,
    Text,
} from 'react-native';

import TrendingTopic from './trendingTopic.js';


const styles = {
  trendingTopicsContainer: {
    flex: 1,
    alignItems: 'center',
    padding: 10,
  },
  trendingTopicsText: {
    textAlign: 'center',
    fontSize: 24,
    padding: 20,
  },
};

export default class TrendingTopics extends Component {
  render() {
    return (
            <View style={styles.trendingTopicsContainer}>
                <Text style={styles.trendingTopicsText}>
                    Trending Topics
                </Text>
                <TrendingTopic name={this.props.topics[0]} onTopicPress={this.props.onTopicPress} />
                <TrendingTopic name={this.props.topics[1]} onTopicPress={this.props.onTopicPress} />
                <TrendingTopic name={this.props.topics[2]} onTopicPress={this.props.onTopicPress} />
                <TrendingTopic name={this.props.topics[3]} onTopicPress={this.props.onTopicPress} />
                <TrendingTopic name={this.props.topics[4]} onTopicPress={this.props.onTopicPress} />
                <TrendingTopic name={this.props.topics[5]} onTopicPress={this.props.onTopicPress} />
                <TrendingTopic name={this.props.topics[6]} onTopicPress={this.props.onTopicPress} />

            </View>
        );
  }
}
