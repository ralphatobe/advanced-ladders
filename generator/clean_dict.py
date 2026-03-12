#!/usr/bin/env python3
"""
Script to remove words shorter than a given length from a dictionary file.
The dictionary file should have one word per line.
"""

import argparse
import sys
import tempfile
import shutil


def filter_words_by_length(input_file, output_file, min_length=None, max_length=None):
    """
    Filter words in the input file by length and write to the output file.
    
    Args:
        input_file: Path to input dictionary file
        output_file: Path to output filtered dictionary file
        min_length: Minimum length of words to keep (inclusive)
        max_length: Maximum length of words to keep (inclusive)
    """
    if not min_length and not max_length:
        print("No length constraints provided. Exiting without changes.")
        return

    input_extension = input_file.split('.')[-1].lower()
    
    filtered_count = 0
    total_count = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            # Skip header if CSV
            if input_extension == 'csv':
                header = infile.readline()
                outfile.write(header)

            for line in infile:
                total_count += 1

                if input_extension == 'csv':
                    word = line.split(',')[0].strip()
                else:
                    word = line.strip()
                
                # Keep words that meet the length requirement(s)
                if ((min_length is None or len(word) >= min_length) and (max_length is None or len(word) <= max_length)):
                    if input_extension == 'csv':
                        outfile.write(line)
                    else:
                        outfile.write(word + '\n')
                    filtered_count += 1
        
        removed_count = total_count - filtered_count
        print(f"Processing complete!")
        print(f"Total words processed: {total_count}")
        print(f"Words kept: {filtered_count}")
        print(f"Words removed: {removed_count}")
        print(f"Output written to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except IOError as e:
        print(f"Error: IO operation failed - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred - {e}")
        sys.exit(1)


def filter_words_by_reference(input_file, output_file, reference_file):
    """
    Filter words in the input file based on a reference dictionary file.
    
    Args:
        input_file: Path to input dictionary file
        output_file: Path to output filtered dictionary file
        reference_file: Path to reference dictionary file
    """
    input_extension = input_file.split('.')[-1].lower()

    try:
        with open(reference_file, 'r', encoding='utf-8') as ref_file:
            reference_words = set(word.strip() for word in ref_file if word.strip())
        
        filtered_count = 0
        total_count = 0
        
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line in infile:
                total_count += 1
                if input_extension == 'csv':
                    word = line.split(',')[0].strip()
                else:
                    word = line.strip()
                
                if word in reference_words:
                    if input_extension == 'csv':
                        outfile.write(line)
                    else:
                        outfile.write(word + '\n')
                    filtered_count += 1
        
        removed_count = total_count - filtered_count
        print(f"Processing complete!")
        print(f"Total words processed: {total_count}")
        print(f"Words kept: {filtered_count}")
        print(f"Words removed: {removed_count}")
        print(f"Output written to: {output_file}")
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except IOError as e:
        print(f"Error: IO operation failed - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred - {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Remove words shorter than a given length from a dictionary file.'
    )
    parser.add_argument(
        'input_file',
        help='Path to the input dictionary file (one word per line)'
    )
    parser.add_argument(
        'output_file',
        help='Path to the output filtered dictionary file'
    )
    parser.add_argument(
        '--min_length',
        type=int,
        help='Minimum word length to keep (words shorter than this will be removed)'
    )
    parser.add_argument(
        '--max_length',
        type=int,
        help='Maximum word length to keep (words longer than this will be removed)'
    )
    parser.add_argument(
        '--reference_file',
        type=str,
        help='Path to a reference dictionary file; only words present in this file will be kept'
    )
    parser.add_argument(
        '--in-place',
        action='store_true',
        help='Modify the input file in place (output_file argument will be ignored)'
    )
    
    args = parser.parse_args()
    
    # Validate minimum length
    if args.min_length < 1:
        print("Error: Minimum length must be at least 1.")
        sys.exit(1)
    
    # Handle in-place modification
    if args.in_place:
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        temp_filename = temp_file.name
        temp_file.close()
        
        # Filter to temporary file
        filter_words_by_length(args.input_file, temp_filename, args.min_length)

        if args.reference_file:
            # Further filter by reference file
            intermediate_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
            intermediate_filename = intermediate_file.name
            intermediate_file.close()
            
            filter_words_by_reference(
                temp_filename,
                intermediate_filename,
                args.reference_file
            )
            
            # Replace temp file with intermediate results
            shutil.move(intermediate_filename, temp_filename)
        
        # Replace original file with filtered version
        try:
            shutil.move(temp_filename, args.input_file)
            print(f"In-place modification complete: {args.input_file}")
        except Exception as e:
            print(f"Error replacing original file: {e}")
            sys.exit(1)
    else:
        filter_words_by_length(args.input_file, args.output_file, args.min_length, args.max_length)

        if args.reference_file:
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
            temp_filename = temp_file.name
            temp_file.close()
            
            filter_words_by_reference(
                args.output_file,
                temp_filename,
                args.reference_file
            )

            # Replace output file with filtered version
            try:
                shutil.move(temp_filename, args.output_file)
                print(f"Filtered by reference file complete: {args.output_file}")
            except Exception as e:
                print(f"Error replacing output file: {e}")
                sys.exit(1)



if __name__ == '__main__':
    main()