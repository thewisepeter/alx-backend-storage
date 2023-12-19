#!/usr/bin/env python3
'''
    Write a Python script that provides some stats about
    Nginx logs stored in MongoDB:

    Database: logs
    Collection: nginx
    Display (same as the example):
    first line: x logs where x is the number of documents in
    this collection
    second line: Methods:
    5 lines with the number of documents with the method =
    ["GET", "POST", "PUT", "PATCH", "DELETE"] in this order
    (see example below - warning: it’s a tabulation before each line)
    one line with the number of documents with:
    method=GET
    path=/status
'''


def print_nginx_stats(nginx_logs):
    ''' function that gives stats about Nginx logs '''
    print(f"{nginx_logs.estimated_document_count()} logs")

    print("Methods:")
    for method in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
        count = nginx_logs.count_documents({"method": method})
        print(f"\tmethod {method}: {count}")

    number_of_gets = nginx_logs.count_documents(
        {"method": "GET", "path": "/status"})
    print(f"{number_of_gets} status check")

if __name__ == "__main__":
    mongo_collection = MongoClient('mongodb://127.0.0.1:27017').logs.nginx
    print_nginx_stats(nginx_logs)
