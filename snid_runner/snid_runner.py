# -*- coding: utf-8 -*-
"""
Created on Wed 16 2016
Automating SNID for batch use to select redshift, type and age.
Should work for any type but only tested for Ia's.
@author: astrobarn
"""
import glob
import os
import collections
import warnings

import numpy as np

class SNID_output(object):
    '''
    Parsing SNID output file.
    '''
    def __init__(self, snid_file):
        self.sn_types = dict()
        self.templates = []

        self._parse(snid_file)

    def _parse(self, snid_file):
        f = open(snid_file)
        counter = 0
        # Read away the header
        while counter < 5:
            line = f.readline()
            if line.startswith('###'):
                counter += 1
        f.readline()

        sn_type_info = collections.namedtuple('SNID_type_info', 'type ntemp fraction slope redshift redshift_error age age_error'.split(' '))
        for line in f:
            if not line.startswith('Ia'):
                break
            line = line.split()
            self.sn_types[line[0]] = sn_type_info(type=line[0], ntemp=int(line[1]),
                                                  **dict((x, float(y)) for x, y in
                                                  zip('fraction slope redshift redshift_error age age_error'.split(' '),
                                                      line[2:])))
        # Skip the rest
        # NOTE: other types should be read here.
        for line in f:
            if line.startswith('#no.'):
                break

        template_info = collections.namedtuple('SNID_template_info', 'sn type lap rlap z zerr age age_flag grade'.split())
        for line in f:
            if line.startswith('#'):
                continue # Or maybe you want to stop as it is the r-lap cutoff?

            line = line.split()[1:]
            try:
                self.templates.append(template_info(sn=line[0], type=line[1], lap=float(line[2]), rlap=float(line[3]),
                                                z=float(line[4]), zerr=float(line[5]),
                                                age=float(line[6]), age_flag=bool(line[7]), grade=line[8]))
            except ValueError:
                pass

    def select_best_redshift(self, cutoff=5):
        '''
        Compute the median of redshifts over the cutoff and estimate the errors in two ways.

        '''
        z = [t.z for t in self.templates if t.rlap >= cutoff and t.grade == 'good']
        zerr = [t.zerr for t in self.templates if t.rlap >= cutoff and t.grade == 'good']

        return np.median(z), np.std(z), np.mean(zerr)

    def select_best_type(self, cutoff=5):
        types = collections.Counter(t.type for t in self.templates if t.rlap >=cutoff and t.grade == 'good')
        return types.most_common(1)[0][0]

    def select_best_age(self, cutoff=5):
        types = collections.Counter(t.age for t in self.templates if t.rlap >= cutoff and t.grade == 'good')
        return types.most_common(1)[0][0]

def run_snid(spectrum):
    original_path = os.getcwd()
    command = 'snid plot=0 inter=0 ' + os.path.abspath(spectrum) + '>/dev/null'
    os.system('mkdir -p /tmp/snid_temp')
    os.chdir('/tmp/snid_temp')
    ret = os.system(command)
    if ret != 0:
        raise RuntimeError('SNID returned with error {}'.format(ret))
    try:
        snid_output = glob.glob('*output')[0]
    except IndexError:
        raise RuntimeError('SNID found no template')

    sn = SNID_output(snid_output)
    os.system('rm /tmp/snid_temp/*')
    os.chdir(original_path)
    return sn

