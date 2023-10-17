# Name: gitlab_convention_verifyer
# Author: GE-P
# Creation date: 09/08/2022
# Modification date: 24/08/2022
# Version: 0.9
""" Script to verify if all the projects and groups follow convention """
# ------------------------------------------------------------
import os
import gitlab
import urllib3
from colorama import Fore
import inflection
import pymsteams
from dotenv import load_dotenv

# Opening our .env
load_dotenv()

# All the secret variables stored inside .env file
gitlab_url = os.environ.get('gitlab_url')
token = os.environ.get('private_token')
teams_url = os.environ.get('teams_url')

# ------- Auto Correction ------- #
auto_correction = 0               # Change this to 1 if you want autocorrection to be on
# ------------------------------- #

gl = gitlab.Gitlab(url=gitlab_url, private_token=token, ssl_verify=False)

urllib3.disable_warnings()


# Function that scans all members from a group
def find_group_member(group):
    global user_list
    user_list = []
    groups = gl.groups.list(all=True)
    for grp in groups:
        if grp.name == group.name:
            try:
                members = grp.members.list(all=True)
                for member in members:
                    print("Member : " + str(member.name))
                    user_list.append(member.name)

            except:
                # Authorisation error handler - lack of privileges
                print(Fore.RED + "Not allowed" + Fore.RESET)


# Function to verify and change groups name, accordingly with convention
def camelcase(group):
    bad_name = 0
    left_word, right_word = "", ""
    name = group.name
    camel_name = inflection.camelize(name)
    for char in name:
        if char == " ":
            bad_name += 1
            listed_name = name.split()
            left_word = inflection.camelize(listed_name[0])
            right_word = inflection.camelize(listed_name[1])
        elif char == "_":
            bad_name += 1
            listed_name = name.split("_")
            left_word = inflection.camelize(listed_name[0])
            right_word = inflection.camelize(listed_name[1])
    if bad_name != 0:
        print(Fore.RED + "Group name convention not respected" + Fore.RESET)
        good_name = left_word + right_word
        print("Group name awaited : " + good_name)
        if auto_correction == 1:
            groups = gl.groups.list(all=True)
            for grp in groups:
                if grp.name == name:
                    grp.name = good_name
                    grp.path = good_name
                    grp.save()
            print(Fore.BLUE + "Group name changed following convention" + Fore.RESET)
    else:
        if name == camel_name:
            print(Fore.GREEN + "Group name convention respected" + Fore.RESET)
        else:
            print(Fore.RED + "Group name convention not respected" + Fore.RESET)
            print("Group name awaited : " + camel_name)
            if auto_correction == 1:
                groups = gl.groups.list(all=True)
                for grp in groups:
                    if grp.name == name:
                        grp.name = camel_name
                        grp.path = camel_name
                        grp.save()
                print(Fore.BLUE + "Group name changed following convention" + Fore.RESET)


# Function to verify and change projects name, accordingly with convention
def snakecase(project):
    first_char = project.name[:1]
    if first_char == "_":
        project.name = project.name[1:]

# Optional ---------------------------------------------------------------------------------------------------------- #
    # project_snake_1 = inflection.parameterize(project.name)   # 1- We add dashes to all special characters as spaces
    # project_snake_2 = inflection.camelize(project_snake_1)    # 2- Then we add the uppercase to all first letters
    # project_snake_3 = inflection.underscore(project_snake_2)  # 3- Finally we add the underscore who are != uppercase
# Optional ---------------------------------------------------------------------------------------------------------- #

    project_snake_3 = inflection.underscore(project.name)       # If it is snake_cased no need for upper lines
    print("# Name awaited : " + project_snake_3)
    if project.name != project_snake_3:
        print(Fore.RED + "Name convention not respected" + Fore.RESET)
        if auto_correction == 1:
            project.name = project_snake_3
            project.path = project.name
            project.save()
            print(Fore.BLUE + "Name and path changed following convention" + Fore.RESET)
    else:
        print(Fore.GREEN + "Name convention is respected" + Fore.RESET)


# This is the main function, list all projects + groups + members + tree structure and count bad ones + teams report
def list_projects():
    project_struct, project_count, project_bad_count = 0, 0, 0
    url = ""  # Add your documentation source url here 
    projects = gl.projects.list(all=True)

    for project in projects:
        project_bad = 0
        print("#------------------------------------#\n"
              "# Project name : " + project.name + "\n"
              "#------------------------------------#")

        snakecase(project)
        groups = project.groups.list(all=True)

        for group in groups:
            print("--> Group name : " + group.name)
            camelcase(group)
            if group == groups[0]:
                find_group_member(group)
        branches = project.branches.list(all=True)

        for branch in branches:
            file, folder = 0, 0
            print("Branch name : " + branch.name)
            objects = project.repository_tree('.', ref=branch.name, all=True)

            for obj in objects:
                obj_name = obj['name']
                obj_type = obj['type']

                if obj_type == "tree":
                    print("    --/ " + obj['name'] + " " + obj['type'])
                else:
                    print("        --| " + obj['name'] + " " + obj['type'])

                if obj_type == "blob" and obj_name == "README.md":
                    file += 1
                elif obj_type == "blob" and obj_name == "CHANGELOG":
                    file += 1
                elif obj_type == "blob" and obj_name == ".gitignore":
                    file += 1
                elif obj_type == "tree" and obj_name == "src":
                    folder += 1
                elif obj_type == "tree" and obj_name == "docs":
                    folder += 1
                elif obj_type == "tree" and obj_name == "test-files":
                    folder += 1

            if file >= 3 and folder >= 3:
                print(Fore.GREEN + "Branch structure is OK" + Fore.RESET)
                project_struct += 1
            else:
                print(Fore.RED + "Branch structure not accepted" + Fore.RESET)
                project_bad += 1

        if project_bad > 0:
            print("#------------------------------------------#" + "\n"
                  "# --> Project: " + project.name + Fore.RED + " Structure is not validated" + Fore.RESET)
            project_bad_count += 1
            print("# --> Users to report: " + str(user_list) + "\n"
                  "#------------------------------------------#" + "\n\n")

            for user in user_list:
                file = open("./reports/" + str(user) + ".txt", "a")
                file.write(str(project.name) + "\n")
                file.close()

            teams_msg = pymsteams.connectorcard(teams_url)

            teams_msg.title("- Bad Project Structure -")
            teams_msg.text("# - Project : " + project.name + " --> Structure is not validated" + "\n"
                           "# - Users to report : " + str(user_list) + "\n")
            teams_msg.addLinkButton("Open convention wiki", url)
            teams_msg.color('EA680F')
            teams_msg.send()

        else:
            print("#------------------------------------------#" + "\n"
                  "# --> Project: " + project.name + Fore.GREEN + " Structure is validated" + Fore.RESET + "\n"
                  "#------------------------------------------#" + "\n\n")

        project_count += 1

    print("-----------------------------------\n"
          "| Projects number : " + str(project_count) + "\n"
          "-----------------------------------")
    print("| Validated projects structure : " + str(project_count - project_bad_count) + "\n"
          "-----------------------------------")


if __name__ == "__main__":
    list_projects()
