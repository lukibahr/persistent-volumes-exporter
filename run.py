#!/usr/bin/env python
"""
Main program
"""

import time
import argparse
import logging
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server
from kubernetes import client, config

LOGFORMAT = "%(asctime)s - %(levelname)s [%(name)s] %(threadName)s %(message)s"

class CustomCollector():
    """
    Class CustomCollector implements the collect function
    """
    def __init__(self, cfg=None):
        try:
            logging.info("Trying to load in-cluster config")
            config.load_incluster_config()
        except:
            # ToDo: handle exception
            logging.info("Loading in-cluster configuration failed, falling back to file %s", cfg)
            config.load_kube_config(cfg)
        self.v1 = client.CoreV1Api()

    def collect(self):
        """collect collects the metrics"""
        released = GaugeMetricFamily("kubernetes_persistent_volumes_released",
                            'Kubernetes persistent volumes in release state',
                            labels=['name','phase','capacity','creation_timestamp'])
        bound = GaugeMetricFamily("kubernetes_persistent_volumes_bound",
                            'Kubernetes persistent volumes in bound state',
                            labels=['name','phase','capacity','creation_timestamp'])

        res = self.v1.list_persistent_volume(watch=False)
        for v in res.items:
            logging.debug("found pvc, name:%s status:%s creation_timestamp:%s capacity:%s ",
                          v.metadata.name, v.status.phase, v.metadata.creation_timestamp,
                          v.spec.capacity["storage"])
                          #v.spec.vsphere_volume.volume_path)
            if v.status.phase == "Released":
                released.add_metric([v.metadata.name, v.status.phase, v.spec.capacity["storage"],
                            str(v.metadata.creation_timestamp)], 1)
                yield released
            if v.status.phase == "Bound":
                bound.add_metric([v.metadata.name, v.status.phase, v.spec.capacity["storage"],
                            str(v.metadata.creation_timestamp)], 1)
                yield bound

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='persistent volumes exporter')
    parser.add_argument('-p', '--port', type=int, help='The port, the exporter runs on',
                        default=9123)
    parser.add_argument('-k', '--kubeconfig', type=str, help='Path to kubeconfig file',
                        default="none")
    parser.add_argument("-l", "--loglevel",
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default="INFO", help="Set the logging level")
    args = parser.parse_args()
    if args.loglevel:
        logging.basicConfig(level=getattr(logging, args.loglevel),
                            format=LOGFORMAT)
    logging.debug("Parsing command line arguments: %s", args)
    logging.info("Running exporter on port %s", args.port)
    start_http_server(args.port)
    REGISTRY.register(CustomCollector(args.config))
    while True:
        time.sleep(60)
