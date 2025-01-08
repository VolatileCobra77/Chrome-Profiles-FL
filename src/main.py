import json
import sys
import webbrowser
import subprocess
import os
import re

class FlowLauncherPlugin:
    def __init__(self):
        self.profiles_path = os.path.join(os.path.dirname(__file__), 'profiles.json')

    def query(self, query):
        instructions = query.split(" ")
        if instructions[0] in ["add", "remove", "help", "rename"]:
            if instructions[0] == "add":
                if len(instructions) > 3:
                    profile_name = instructions[1]
                    remaining_query = " ".join(instructions[2:])
                    profile_id = self.parse_id(remaining_query)
                    profile_desc = remaining_query.replace(f'"{profile_id}"', '').replace(profile_id, '').strip()
                    return {"result": [{
                        "Title": f"Add Profile {profile_name}",
                        "SubTitle": f"Add a profile with the name {profile_name} and description {profile_desc}. ID: {profile_id}",
                        "IcoPath": "Images/app.png",
                        "JsonRPCAction": {
                            "method": "add_profile",
                            "parameters": [profile_name, profile_desc, profile_id],
                            "dontHideAfterAction": False
                        }
                    }]}
                else:
                    return {"result": [{
                        "Title": "Invalid Arguments",
                        "SubTitle": "Please provide a name, ID, and description for the profile. Type 'help' for help.",
                        "IcoPath": "Images/app.png"
                    }]}
            elif instructions[0] == "remove":
                if len(instructions) > 1:
                    return {"result": [{
                        "Title": f"Remove Profile {instructions[1]}",
                        "SubTitle": f"Remove the profile with the name {instructions[1]}",
                        "IcoPath": "Images/app.png",
                        "JsonRPCAction": {
                            "method": "remove_profile",
                            "parameters": [instructions[1]],
                            "dontHideAfterAction": False
                        }
                    }]}
                else:
                    return {"result": [{
                        "Title": "Invalid Arguments",
                        "SubTitle": "Please provide a name for the profile to remove. Type 'help' for help.",
                        "IcoPath": "Images/app.png",
                        "JsonRPCAction": {
                            "method": "no_action",
                            "parameters": [],
                            "dontHideAfterAction": True
                        }
                    }]}
            elif instructions[0] == "rename":
                if len(instructions) > 2:
                    return {"result": [{
                        "Title": f"Rename Profile {instructions[1]} to {instructions[2]}",
                        "SubTitle": f"Rename the profile with the name {instructions[1]} to {instructions[2]}",
                        "IcoPath": "Images/app.png",
                        "JsonRPCAction": {
                            "method": "rename_profile",
                            "parameters": [instructions[1], instructions[2]],
                            "dontHideAfterAction": False
                        }
                    }]}
                else:
                    return {"result": [{
                        "Title": "Invalid Arguments",
                        "SubTitle": "Please provide a name for the profile to rename and a new name. Type 'help' for help.",
                        "IcoPath": "Images/app.png",
                        "JsonRPCAction": {
                            "method": "no_action",
                            "parameters": [],
                            "dontHideAfterAction": True
                        }}]}
            elif instructions[0] == "help":
                return {"result": [{
                    "Title": "Help",
                    "SubTitle": "add <name> <id> <description> - Add a profile\nremove <name> - Remove a profile",
                    "IcoPath": "Images/app.png",
                    "JsonRPCAction": {
                            "method": "no_action",
                            "parameters": [],
                            "dontHideAfterAction": True
                        }
                }, {
                    "Title": "More info",
                    "SubTitle": "Add a profile to desktop, then right click > properties > path. \n Look for the '--profile-directory=\"value\"' flag and copy the value.",
                    "IcoPath": "Images/app.png",
                    "JsonRPCAction": {
                            "method": "no_action",
                            "parameters": [],
                            "dontHideAfterAction": True
                        }
                }]}

        profiles = json.loads(open(self.profiles_path).read())
        profiles = [profile for profile in profiles if query.lower() in profile["Title"].lower()]
        if not profiles:
            profiles = [{
                "Title": "No Profiles Found",
                "SubTitle": "No profiles found matching the search criteria",
                "IcoPath": "Images/app.png",
                "JsonRPCAction": {
                    "method": "no_action",
                    "parameters": [],
                    "dontHideAfterAction": True
                }
            }]
        return {"result": profiles}

    def open_url(self, url):
        webbrowser.open(url)

    def open_profile(self, profile_name):
        subprocess.Popen([r"C:\Program Files\Google\Chrome\Application\chrome.exe", f"--profile-directory={profile_name}"])

    def add_profile(self, profile_name, profile_desc, profile_id):
        profiles = json.loads(open(self.profiles_path).read())
        profiles.append({
            "Title": profile_name,
            "SubTitle": profile_desc,
            "IcoPath": "Images/app.png",
            "JsonRPCAction": {
                "method": "open_profile",
                "parameters": [profile_id],
                "dontHideAfterAction": False
            }
        })
        with open(self.profiles_path, "w") as f:
            f.write(json.dumps(profiles, indent=4))

    def remove_profile(self, profile_name):
        profiles = json.loads(open(self.profiles_path).read())
        profiles = [profile for profile in profiles if profile["Title"] != profile_name]
        with open(self.profiles_path, "w") as f:
            f.write(json.dumps(profiles, indent=4))

    def rename_profile(self, profile_name, new_name):
        profiles = json.loads(open(self.profiles_path).read())
        for profile in profiles:
            if profile["Title"] == profile_name:
                profile["Title"] = new_name
        with open(self.profiles_path, "w") as f:
            f.write(json.dumps(profiles, indent=4))

    def parse_id(self, id_string):
        # Regular expression to match quoted or unquoted IDs
        pattern = r'(?<!\\)"(.*?)"|(\S+)'
        match = re.search(pattern, id_string)
        if match:
            return match.group(1) if match.group(1) else match.group(2)
        return None

if __name__ == "__main__":
    plugin = FlowLauncherPlugin()
    if len(sys.argv) > 1:
        request = json.loads(sys.argv[1])
        method_name = request["method"]
        params = request["parameters"]
        method = getattr(plugin, method_name)
        result = method(*params)
        if result:
            print(json.dumps(result))