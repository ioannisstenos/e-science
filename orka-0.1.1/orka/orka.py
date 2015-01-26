#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""orka.orka: provides entry point main()."""
import logging
import os
from sys import argv
from os.path import join, dirname, abspath
from kamaki.clients import ClientError
from cluster_errors_constants import *
from create_cluster import YarnCluster
from okeanos_utils import destroy_cluster, get_user_clusters
from argparse import ArgumentParser, ArgumentTypeError
from version import __version__


class _ArgCheck(object):
    """
    Used for type checking arguments supplied for use with type= and
    choices= argparse attributes
    """

    def __init__(self):
        self.logging_levels = {
            'critical': logging.CRITICAL,
            'error': logging.ERROR,
            'warning': logging.WARNING,
            'summary': SUMMARY,
            'report': REPORT,
            'info': logging.INFO,
            'debug': logging.DEBUG,
        }
        logging.addLevelName(REPORT, "REPORT")
        logging.addLevelName(SUMMARY, "SUMMARY")

    def unsigned_int(self, val):
        """
        :param val: int
        :return: val if val > 0 or raise exception
        """
        ival = int(val)
        if ival <= 0:
            raise ArgumentTypeError(" %s must be a positive number." % val)
        return ival

    def two_or_bigger(self, val):
        """
        :param val: int
        :return: val if > 2 or raise exception
        """
        ival = int(val)
        if ival < 2:
            raise ArgumentTypeError(" %s must be at least 2." % val)
        return ival

    def five_or_bigger(self, val):
        ival = int(val)
        if ival < 5:
            raise ArgumentTypeError(" %s must be at least 5." % val)
        return ival


class HadoopCluster(object):
    """Wrapper class for YarnCluster."""
    def __init__(self, opts):
        self.opts = opts

    def create(self):
        """ Method for creating Hadoop clusters in~okeanos."""
        try:
            c_yarn_cluster = YarnCluster(self.opts)
        except Exception, e:
            logging.error(' Fatal error: ' + str(e.args[0]))
            exit(error_fatal)

        try:
            c_yarn_cluster.create_yarn_cluster()

        except Exception:
            exit(error_fatal)

    def destroy(self):
        """ Method for deleting Hadoop clusters in~okeanos."""
        try:
            destroy_cluster(self.opts['token'], self.opts['master_ip'])
        except ClientError, e:
            logging.error(' Error:' + e.message)
            exit(error_fatal)
        except Exception, e:
            logging.error(' Error:' + str(e.args[0]))
            exit(error_fatal)

from collections import OrderedDict
def custom_sort_factory(order_list):
    """ 
    function factory: gets a list of lists with order keys
    and returns a function that will produce an OrderedDict
    with the specified order.
    Keys not present in the sort list are returned at the end.
    Example:
        fruits = {'apple': 'red', 'orange': 'orange', 'lemon': 'yellow', 'banana': 'yellow'}
        order_list = [['lemon','orange','banana','apple']]
        sort_function = custom_sort_factory(order_list)
        sorted_fruits = sort_function(fruits)
        print fruits
        print sorted_fruits
    """
    order_list = [{k: -i for (i, k) in enumerate(reversed(order), 1)} for order in order_list]
    def sorter(stuff):
        if isinstance(stuff, dict):
            l = [(k, sorter(v)) for (k, v) in stuff.iteritems()]
            keys = set(stuff)
            for order in order_list:
                if keys.issuperset(order):
                    return OrderedDict(sorted(l, key=lambda x: order.get(x[0], 0)))
            return OrderedDict(sorted(l))
        if isinstance(stuff, list):
            return [sorter(x) for x in stuff]
        return stuff
    return sorter


class UserClusterInfo(object):
    """ Class holding user cluster info
    sort: input clusters output cluster keys sorted according to spec
    list: pretty printer
    """
    def __init__(self, opts):
        self.opts = opts
        self.data = list()
        self.order_list = [['cluster_name','cluster_size','cluster_status','master_IP',
                            'project_name','id','os_image','disk_template',
                            'cpu_master','mem_master','disk_master',
                            'cpu_slaves','mem_slaves','disk_slaves']]
        self.sort_func = custom_sort_factory(self.order_list)
        self.short_list = {'cluster_name':True, 'cluster_size':True, 'cluster_status':True, 'master_IP':True}
        self.skip_list = {'id':True}
        self.status_desc_to_status_id = {'ACTIVE':'1', 'PENDING':'2', 'DESTROYED':'0'}
        self.status_id_to_status_desc = {'1':'ACTIVE', '2':'PENDING', '0':'DESTROYED'}
        
    def sort(self, clusters):
        return self.sort_func(clusters)
    
    def list(self):
        try:
            self.data.extend(get_user_clusters(self.opts['token']))
        except ClientError, e:
            logging.error(e.message)
            exit(error_fatal)
        except Exception, e:
            logging.error(str(e.args[0]))
            exit(error_fatal)
        
        opt_short = not self.opts['verbose']
        opt_status = False
        if self.opts['status']:
            opt_status = self.status_desc_to_status_id[self.opts['status'].upper()]
        
        if len(self.data) > 0:
            for cluster in self.data:
                if opt_status and cluster['cluster_status'] != opt_status:
                    continue
                sorted_cluster = self.sort(cluster)
                for key in sorted_cluster:
                    if (opt_short and not self.short_list.has_key(key)) or self.skip_list.has_key(key):
                        continue
                    if key == 'cluster_name':
                        fmt_string = '{:<5}' + key + ': {' + key + '}'
                    elif key == 'cluster_status':
                        fmt_string = '{:<10}' + key + ': ' + self.status_id_to_status_desc[sorted_cluster[key]]
                    else:
                        fmt_string = '{:<10}' + key + ': {' + key + '}'
                    print fmt_string.format('',**sorted_cluster)
                print ''
        else:
            print 'User has no Cluster Information available.'

def main():
    """
    Entry point of orka package. Parses user arguments and return
    appropriate messages for success or error.
    """
    parser = ArgumentParser(description='Create or Destroy a Hadoop-Yarn'
                                        ' cluster in ~okeanos')
    checker = _ArgCheck()
    subparsers = parser.add_subparsers(help='Choose Hadoop cluster action'
                                            ' create or destroy')
    parser.add_argument("-V", "--version", action='version',
                        version=('orka %s' % __version__))
    parser_c = subparsers.add_parser('create',
                                     help='Create a Hadoop-Yarn cluster'
                                     ' on ~okeanos.')
    parser_d = subparsers.add_parser('destroy',
                                     help='Destroy a Hadoop-Yarn cluster'
                                     ' on ~okeanos.')
    parser_i = subparsers.add_parser('list',
                                     help='List user clusters.')
    
    if len(argv) > 1:

        parser_c.add_argument("name", help='The specified name of the cluster.'
                              ' Will be prefixed by a timestamp')

        parser_c.add_argument("cluster_size", help='Total number of cluster nodes',
                              type=checker.two_or_bigger)

        parser_c.add_argument("cpu_master", help='Number of CPU cores for the master node',
                              type=checker.unsigned_int)

        parser_c.add_argument("ram_master", help='Size of RAM (MB) for the master node',
                              type=checker.unsigned_int)

        parser_c.add_argument("disk_master", help='Disk size (GB) for the master node',
                              type=checker.five_or_bigger)

        parser_c.add_argument("cpu_slave", help='Number of CPU cores for the slave node(s)',
                              type=checker.unsigned_int)

        parser_c.add_argument("ram_slave", help='Size of RAM (MB) for the slave node(s)',
                              type=checker.unsigned_int)

        parser_c.add_argument("disk_slave", help='Disk size (GB) for the slave node(s)',
                              type=checker.five_or_bigger)

        parser_c.add_argument("disk_template", help='Disk template (choices: {%(choices)s})',
                              metavar='disk_template', choices=['drbd', 'ext_vlmc'])

        parser_c.add_argument("token", help='Synnefo authentication token')

        parser_c.add_argument("project_name", help='~okeanos project name'
                              ' to request resources from ')

        parser_c.add_argument("--image", help='OS for the cluster.'
                              ' Default is "Debian Base"', metavar='image',
                              default=default_image)

        parser_c.add_argument("--use_hadoop_image", help='Use a pre-stored hadoop image for the cluster.'
                              ' Default is HadoopImage (overrides image selection)',
                              nargs='?', metavar='hadoop_image_name', default=None,
                              const='HadoopBase')

        parser_c.add_argument("--auth_url", metavar='auth_url', default=auth_url,
                              help='Synnefo authentication url. Default is ' +
                              auth_url)

        parser_c.add_argument("--logging", default=default_logging,
                              choices=checker.logging_levels.keys(),
                              help='Logging Level. Default: summary')

        parser_d.add_argument('master_ip',
                              help='The public ip of the master vm of the cluster')
        parser_d.add_argument('token',
                              help='Synnefo authentication token')

        parser_d.add_argument("--logging", default=default_logging,
                              choices=checker.logging_levels.keys(),
                              help='Logging Level. Default: summary')
        
        parser_i.add_argument('token',
                              help='Synnefo authentication token')
        
        parser_i.add_argument('--status', help='Filter by status ({%(choices)s})'
                              ' Default is all: no filtering.', type=str.upper,
                              metavar='status', choices=['ACTIVE','DESTROYED','PENDING'])
        parser_i.add_argument('--verbose', help='List extra cluster details.',
                              action="store_true")
        parser_i.add_argument("--logging", default=default_logging,
                              choices=checker.logging_levels.keys(),
                              help='Logging Level. Default: summary')

        opts = vars(parser.parse_args(argv[1:]))
        if argv[1] == 'create':
            if opts['use_hadoop_image']:
                opts['image'] = opts['use_hadoop_image']
            
        if opts['logging'] == 'debug':
            log_directory = os.getcwd()
            log_file_path = join(log_directory, "create_cluster_debug.log")

            logging.basicConfig(format='%(asctime)s:%(message)s',
                                filename=log_file_path,
                                level=logging.DEBUG, datefmt='%H:%M:%S')
            print ' Creating Hadoop cluster, logs will' + \
                  ' be appended in create_cluster_debug.log'
        else:
            logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                                level=checker.logging_levels[opts['logging']],
                                datefmt='%H:%M:%S')

    else:
        logging.error('No arguments were given')
        parser.parse_args(' -h'.split())
        exit(error_no_arguments)
    c_hadoopcluster = HadoopCluster(opts)
    if argv[1] == 'create':
        c_hadoopcluster.create()

    elif argv[1] == 'destroy':
        c_hadoopcluster.destroy()
        
    elif argv[1] == 'list':
        c_userclusters = UserClusterInfo(opts)
        c_userclusters.list()

if __name__ == "__main__":
    main()