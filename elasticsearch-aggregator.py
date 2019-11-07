#!/usr/bin/env python3
"""
Collects log entry timestamps from an Elasticsearch instance over
a specific time range, aggregates them by minute, and returns the
higest minute, highest hour and highest day, and the count of the log
entries during them.
"""

import argparse
import json
import elasticsearch
import elasticsearch_dsl


def parse_args():
    """
    Parses comand line arguments for local testing, sets defaults
    for function inside an OpenShift cluster.
    """
    parser = argparse.ArgumentParser(
        description='Aggregate Elasticsearch Log data.')
    parser.add_argument(
        '--host',
        default='https://logging-es',
        type=str,
        action='store',
        help='Host name or IP of the Elasticsearch server.'
    )
    parser.add_argument(
        '--port',
        default=9200,
        type=int,
        action='store',
        help='Port number of the Elasticsearch server.'
    )
    parser.add_argument(
        '--ca_certs',
        default='secret/admin-ca',
        type=str,
        action='store',
        help='Path to the CA certificates file'
    )
    parser.add_argument(
        '--cert',
        default='secret/admin-cert',
        type=str,
        action='store',
        help='Path to the client certificate file'
    )
    parser.add_argument(
        '--key',
        default='secret/admin-key',
        type=str,
        action='store',
        help='Path to the client key file'
    )

    return parser.parse_args()


def connect(args):
    """
    Returns an instance of an Elasticsearch cluster connection.
    """
    return elasticsearch.Elasticsearch(
        [f"{args.host}:{args.port}"],
        use_ssl=True,
        verify_certs=True,
        ca_certs=args.ca_certs,
        client_cert=args.cert,
        client_key=args.key,
    )


def get_indices(client):
    """
    Retrieves a list of indices from the Elasticsearch cluster.
    """

    return [key for (key, _) in client.indices.get('*').items()]



def bucket_by_minute(client, search_index):
    """
    Retrieves buckets by minute.
    """

    # Raw CURL to do this:
    # {
    #     "aggs" : {
    #         "group_by_minute" : {
    #             "date_histogram" : {
    #                 "field" : "@timestamp",
    #                 "interval" : "minute",
    #                 "format" : "yyyy-MM-dd:hh:mm"
    #             }
    #         }
    #     }
    # }'

    search = elasticsearch_dsl.Search(using=client, index=search_index)
    search.aggs.bucket(
        'by_minute',
        'date_histogram',
        field='@timestamp',
        interval='minute')

    response = search.execute()
    buckets = response.aggregations.by_minute.buckets

    count_by_time = {}
    for i in buckets:
        count_by_time[i['key_as_string']] = i['doc_count']

    return count_by_time


if __name__ == "__main__":
    CLIENT = connect(parse_args())
    try:
        CLIENT.cluster.health()
    except elasticsearch.AuthenticationException as err:
        print(err)
    else:
        results = {}
        INDICES = get_indices(CLIENT)
        for index in INDICES:
            results[index] = bucket_by_minute(CLIENT, index)
        print(json.dumps(results, sort_keys=True))
