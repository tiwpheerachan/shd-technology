import json
import requests
import os

def create_thai_provinces_json():
    """
    Create a JSON file with all Thai provinces, districts, and subdistricts.
    This script can be run separately to generate the thai_provinces.json file.
    """
    print("Creating Thai provinces JSON file...")
    
    # Check if file already exists
    if os.path.exists("thai_provinces.json"):
        print("File already exists. Skipping download.")
        return
    
    # URLs for Thai provinces data
    data_url = "https://raw.githubusercontent.com/earthchie/jquery.Thailand.js/master/jquery.Thailand.js/database/raw_database/raw_database.json"
    
    try:
        # Download the data
        print("Downloading data...")
        response = requests.get(data_url)
        if response.status_code == 200:
            # Process the data into our required format
            raw_data = response.json()
            
            # Transform the data into our format
            provinces = {}
            for item in raw_data:
                province = item.get("province", "")
                amphoe = item.get("amphoe", "")
                district = item.get("district", "")
                
                if province not in provinces:
                    provinces[province] = {"name_th": province, "name_en": "", "amphoes": {}}
                
                if amphoe not in provinces[province]["amphoes"]:
                    provinces[province]["amphoes"][amphoe] = {"name_th": amphoe, "name_en": "", "tambons": {}}
                
                if district:
                    provinces[province]["amphoes"][amphoe]["tambons"][district] = {"name_th": district, "name_en": ""}
            
            # Convert to list format
            provinces_list = []
            for p_name, p_data in provinces.items():
                amphoes_list = []
                for a_name, a_data in p_data["amphoes"].items():
                    tambons_list = []
                    for t_name, t_data in a_data["tambons"].items():
                        tambons_list.append(t_data)
                    
                    a_data["tambons"] = tambons_list
                    amphoes_list.append(a_data)
                
                p_data["amphoes"] = amphoes_list
                provinces_list.append(p_data)
            
            # Save to file
            with open("thai_provinces.json", "w", encoding="utf-8") as f:
                json.dump(provinces_list, f, ensure_ascii=False, indent=2)
            
            print(f"Successfully created thai_provinces.json with {len(provinces_list)} provinces")
        else:
            print(f"Failed to download data: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error creating Thai provinces JSON: {e}")

if __name__ == "__main__":
    create_thai_provinces_json()
