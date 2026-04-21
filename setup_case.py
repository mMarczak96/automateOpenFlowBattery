import os
import yaml
import shutil
from jinja2 import Template

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

if __name__ == "__main__":
    update_openfoam_files("test_case", "config.yaml")