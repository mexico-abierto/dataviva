# -*- coding: utf-8 -*-
"""
    Calculate growth for all tables
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

''' Import statements '''
import csv, sys, os, argparse, math, time, bz2
from collections import defaultdict
from os import environ
from os.path import basename, splitext
import pandas as pd
import numpy as np
from ..helpers import get_file, format_runtime
from ..config import DATA_DIR
from ..growth_lib import growth
from scripts import YEAR, DELETE_PREVIOUS_FILE, TABLE, help_text_table

def main(year, delete_previous_file, table):
    index_lookup = {"b":"bra_id", "p":"hs_id", "w":"wld_id"}
    file_lookup = {"yb":"yb_ecis_diversity.tsv", "ybp":"ybp_rcas_dist_opp.tsv", \
                    "ybpw": "ybpw.tsv", "ybw": "ybw.tsv", \
                    "yp": "yp_pcis_diversity_rcas.tsv", \
                    "ypw": "ypw.tsv", "yw": "yw_ecis_diversity.tsv"}
    index_cols = [index_lookup[i] for i in table if i != "y"]
    converters = {"hs_id": str} if "p" in table else None
    prev_year = str(int(year) - 1)
    prev_year_5 = str(int(year) - 5)
    
    print "loading current year"
    current_file_path = os.path.abspath(os.path.join(DATA_DIR, 'secex', year, file_lookup[table]))
    current_file = get_file(current_file_path)
    if not current_file:
        f = splitext(basename(file_lookup[table]))[0] + "_growth.tsv"
        current_file_path = os.path.abspath(os.path.join(DATA_DIR, 'secex', year, f))
        current_file = get_file(current_file_path)
        if not current_file:
            print "Unable to find", current_file_path
            sys.exit()
    current = pd.read_csv(current_file, sep="\t", converters=converters)
    current = current.set_index(index_cols)
    
    print "loading previous year"
    prev_file_path = os.path.abspath(os.path.join(DATA_DIR, 'secex', prev_year, file_lookup[table]))
    prev_file = get_file(prev_file_path)
    if not prev_file:
        f = splitext(basename(file_lookup[table]))[0] + "_growth.tsv"
        prev_file_path = os.path.abspath(os.path.join(DATA_DIR, 'secex', prev_year, f))
        prev_file = get_file(prev_file_path)
        if not prev_file:
            print "Unable to find", prev_file_path
            sys.exit()
    prev = pd.read_csv(prev_file, sep="\t", converters=converters)
    prev = prev.set_index(index_cols)
    
    print "calculating 1 year val_usd growth value"
    s = time.time()
    current["val_usd_growth_val"] = current["val_usd"] - prev["val_usd"]
    print (time.time() - s) / 60
    
    print "calculating 1 year val_usd growth rate"
    s = time.time()
    current["val_usd_growth_rate"] = (current["val_usd"] / prev["val_usd"]) - 1
    print (time.time() - s) / 60
    
    prev_5_file_path = os.path.abspath(os.path.join(DATA_DIR, 'secex', prev_year_5, file_lookup[table]))
    prev_5_file = get_file(prev_5_file_path)
    if not prev_5_file:
        f = splitext(basename(file_lookup[table]))[0] + "_growth.tsv"
        prev_5_file_path = os.path.abspath(os.path.join(DATA_DIR, 'secex', prev_year_5, f))
        prev_5_file = get_file(prev_5_file_path)
    if prev_5_file:
        print "loading file for 5 years ago"
        prev_5 = pd.read_csv(prev_5_file, sep="\t", converters=converters)
        prev_5 = prev_5.set_index(index_cols)
        
        print "calculating 5 year val_usd growth value"
        current["val_usd_growth_val_5"] = current["val_usd"] - prev_5["val_usd"]
    
        print "calculating 5 year val_usd growth rate"
        current["val_usd_growth_rate_5"] = (current["val_usd"] / prev_5["val_usd"]) ** (1.0/5.0) - 1
    
    new_file_name = splitext(basename(file_lookup[table]))[0] + "_growth.tsv.bz2"
    print "writing new growth file..."
    new_file_path = os.path.abspath(os.path.join(DATA_DIR, 'secex', year, new_file_name))
    current.to_csv(bz2.BZ2File(new_file_path, 'wb'), sep="\t", index=True)
    
    if delete_previous_file:
        print "deleting previous file"
        os.remove(current_file.name)

if __name__ == "__main__":
    start = time.time()
    
    if not TABLE:
        TABLE = raw_input(help_text_table)
    
    main(YEAR, DELETE_PREVIOUS_FILE, TABLE)
    
    total_run_time = time.time() - start
    print; print;
    print "Total runtime: " + format_runtime(total_run_time)
    print; print;