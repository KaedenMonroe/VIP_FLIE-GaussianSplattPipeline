import os, argparse


if __name__ == '__main__':
    # Initialize the parser
    parser = argparse.ArgumentParser(description="A simple argument parser")

    # Add arguments
    parser.add_argument("-i", "--input") 
    parser.add_argument("-o", "--output") 
    parser.add_argument("-m", "--metashape_output") 
    parser.add_argument("-n", "--name")

    # Parse the arguments
    args = parser.parse_args()

    if not args.input:
        raise "Error, no input dir provided"
    elif not args.output:
        raise "Error, no ouput dir provided for the colmap data"
    elif not args.metashape_output:
        raise "Error, no output dir provided for the metashape file"
    elif not args.name:
        raise "Error, no output file naming convention"
    
    import_path = args.input
    export_path = args.output
    metashape_directory = args.metashape_output
    name = args.name
    
    # base_dir is project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    #path to metashape_script.py
    script_path = str(os.path.join(base_dir, "scripts", "metashape_script.py"))
    
    #TEMP:Using to test the output without access to metashape
    print(f'"path\\to\\your\\metashape.exe" -r {script_path}" -i "{import_path}" -o "{export_path}" -m "{metashape_directory}" -n "{name}"')