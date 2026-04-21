import os
import re
import yaml
import shutil
import logging
from jinja2 import Template

def get_variable_value(file_content, var_name):
    pattern = rf"{var_name}\s+([\d.]+);"
    match = re.search(pattern, file_content)
    
    if match:
        return float(match.group(1))
    return None

def get_current_density(config_dict):
    
    provided_cc_area = False
    
    if not provided_cc_area:
        print("Calculating CC Area From the blockMeshDict")

        with open('template/system/blockMeshDict', 'r') as f:
            content = f.read()
        
        length = get_variable_value(content, 'length')
        width = get_variable_value(content, 'width')
        convertToMeters = get_variable_value(content, 'convertToMeters')

        cc_patch_area = length * width * convertToMeters * convertToMeters
    else:
        cc_patch_area = 2137 # provide a script input value
    
    Itotal = config_dict['regions']['global']['constant']['batteryControl']['Itotal']

    return Itotal / cc_patch_area / 10

def write_to_log(config_dict):
    
    logger = logging.getLogger("OpenFOAM_Automation")
    logger.setLevel(logging.INFO)

    # Add the Summary File Handler (Saves to file)
    summary_handler = logging.FileHandler("simulation_summary.log")
    summary_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(summary_handler)

    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)

    simType = config_dict['regions']['global']['system']['fvSolution']['controlMethod']
    
    curren_density = 'None'
    if simType == 'galvanostatic':
        curren_density = get_current_density(config_dict)

    U_cell = config_dict['regions']['global']['constant']['batteryControl']['U_cell']
    fluidFlow = config_dict['regions']['global']['system']['fvSolution']['fluidFlow']
    linearizeSourceTerm = config_dict['regions']['global']['system']['fvSolution']['linearizeSourceTerm']


    logger.info(f"- - - - - - - Simulation Setup - - - - - - -")
    logger.info(f"Simulation Type: {simType}")
    logger.info(f"Applied Current Density: {curren_density} mA/cm2")
    logger.info(f"Initial Cell Voltage: {U_cell} V")

    logger.info(f"Fluid Dynamics Equations: {fluidFlow}")
    logger.info(f"Electrolyte Potential Source Term Linearization:: {linearizeSourceTerm}")


def update_openfoam_files(case_name, config_path):
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    regions = config_data.get('regions', {})
    template_dir = 'template' 

    # Prepare case directory
    if os.path.exists(case_name):
        shutil.rmtree(case_name)
    shutil.copytree(template_dir, case_name)
    print(f"Created case: {case_name}")

    # Map YAML categories to disk folders
    folder_map = {
        "initialConditions": "0",
        "constant": "constant",
        "system": "system"
    }

    for region_name, categories in regions.items():
        for category, dictionaries in categories.items():
            
            # Look up the base folder (0, constant, or system)
            base_folder = folder_map.get(category)
            
            if not base_folder:
                print(f"   Warning: Category '{category}' not recognized. Skipping.")
                continue

            # Determine the final path based on global vs regional
            if region_name == "global":
                target_dir = os.path.join(case_name, base_folder)
            else:
                target_dir = os.path.join(case_name, base_folder, region_name)

            # Update the files
            if dictionaries:
                for dict_name, params in dictionaries.items():
                    file_path = os.path.join(target_dir, dict_name)
                    
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            content = f.read()

                        rendered = Template(content).render(**params)
                        
                        with open(file_path, 'w') as f:
                            f.write(rendered)
                        print(f"   Updated: {file_path}")
                    else:
                        print(f"   Warning: File not found: {file_path}")

    write_to_log(config_data)

if __name__ == "__main__":

    update_openfoam_files("test_case", "config.yaml")
    # os.system(f"cd test_case && ./Allrun.sh")