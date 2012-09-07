#!/usr/bin/env python
# File created on 09 Feb 2010

__author__ = "Greg Caporaso"
__copyright__ = "Copyright 2011, The QIIME Project" 
__credits__ = ["Greg Caporaso"] 
__license__ = "GPL"
__version__ = "1.5.0-dev"
__maintainer__ = "Greg Caporaso"
__email__ = "gregcaporaso@gmail.com"
__status__ = "Development"

from os.path import splitext, split, exists, abspath, join
from qiime.util import (make_option, 
                        parse_command_line_parameters, 
                        create_dir, 
                        load_qiime_config,
                        get_qiime_temp_dir)
from qiime.assign_reads_to_database import (usearch_database_mapper, 
                                            blat_database_mapper)

qiime_config = load_qiime_config()

assignment_functions = {'usearch':usearch_database_mapper,
                        'blat':blat_database_mapper}

script_info={}
script_info['brief_description'] = """ Script for performing assignment of reads against a reference database """
script_info['script_description'] = """ """

script_info['script_usage'] = []

script_info['script_usage'].append(("""""","""Run assignment with usearch using default parameters""","""%prog -i query_nt.fasta -r refseqs_pr.fasta"""))

script_info['script_usage'].append(("""""","""Run assignment with BLAT using default parameters""","""%prog -i query_nt.fasta -r refseqs_pr.fasta -m blat"""))

script_info['script_usage'].append(("""""","""Run assignment with BLAT using scricter e-value threshold""","""%prog -i query_nt.fasta -r refseqs_pr.fasta -o blat_mapped_strict/ -e 1e-70  -m blat"""))

script_info['output_description'] = """ """

script_info['required_options'] = [
    make_option('-i', '--input_seqs_filepath',type='existing_filepath',
        help='Path to input sequences file'),

    make_option('-r', '--refseqs_fp',type='existing_filepath',
        help=('Path to reference sequences to search against [default: %default]')),
    ]

script_info['optional_options'] = [
    make_option('-m', '--assignment_method', type='choice',
        choices=assignment_functions.keys(), default = "usearch",
        help=('Method for picking OTUs.  Valid choices are: ' +\
              ', '.join(assignment_functions.keys()) +\
              '. [default: %default]')),

    make_option('-o', '--output_dir',type='new_dirpath',\
        help=('Path to store result file '
              '[default: ./<METHOD>_mapped/]')),
    
    make_option('-e', '--evalue', type='float', default=1e-10,
        help=('Max e-value to consider a match [default: %default]')),
              
    make_option('-s', '--min_percent_id', type='float', default=0.75,
        help=('Min percent id to consider a match [default: %default]')),
              
    make_option('--queryalnfract', type='float', default=0.35,
        help=('Min percent of the query seq that must match to consider a match (usearch only) [default: %default]')),
              
    make_option('--targetalnfract', type='float', default=0.0,
        help=('Min percent of the target/reference seq that must match to consider a match (usearch only) [default: %default]')),

    make_option('--max_accepts',type='int',default=1,
              help="max_accepts value (usearch only) [default: %default]"),
                   
    make_option('--max_rejects',type='int',default=32,
              help="max_rejects value to (usearch only) [default: %default]"),

]

script_info['version'] = __version__

def main():
    # Parse the command line parameters
    option_parser, opts, args =\
        parse_command_line_parameters(**script_info)
    
    # Create local copies of the options to avoid repetitive lookups
    assignment_method = opts.assignment_method
    refseqs_fp = abspath(opts.refseqs_fp)
    input_seqs_filepath = abspath(opts.input_seqs_filepath)
    verbose = opts.verbose
    
    # use the otu_picking_method value to get the otu picker constructor
    assignment_function = assignment_functions[assignment_method]
    
    # create the output directory name (if not provided) and 
    # create it if it doesn't already exist
    output_dir = abspath(opts.output_dir or assignment_method + '_mapped')
    create_dir(output_dir, fail_on_exist=False)
    
    if assignment_method == 'usearch':
        assignment_function(query_fp=input_seqs_filepath,
                               refseqs_fp=refseqs_fp,
                               output_dir=output_dir,
                               evalue=opts.evalue,
                               min_id=opts.min_percent_id,
                               queryalnfract=opts.queryalnfract,
                               targetalnfract=opts.targetalnfract,
                               maxaccepts=opts.max_accepts,
                               maxrejects=opts.max_rejects,
                               HALT_EXEC=False)
    elif assignment_method == 'blat':
        assignment_function(query_fp=input_seqs_filepath,
                               refseqs_fp=refseqs_fp,
                               output_dir=output_dir,
                               evalue=opts.evalue,
                               min_id=opts.min_percent_id,
                               HALT_EXEC=False)
        
    else:
        ## other -- shouldn't be able to get here as a KeyError would have
        ## been raised earlier
        raise ValueError, "Unknown read mapping method: %s" % assignment_method

if __name__ == "__main__":
    main()

