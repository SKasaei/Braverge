from github import Github

from github import GithubIntegration, GithubException
from github import Auth
import networkx as nx
import matplotlib.pyplot as plt
import base64
import uuid # to create uuid
import json
import os


#import sys,os
#sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
#from myBloom import myBloom
from controller.myBloom import myBloom
from controller.ViewManagement import ViewManagement

#from pathlib import Path
#import os

# g= Github("sajadkasaei", "#Sajad123")
# auth = Auth.Login("sajadkasaei", "#Sajad123")
# g = Github(auth=auth)
# g.get_user().login

class myGithub():
    #global GitVar
    def __init__(self, ACCESS_TOKEN):
        super().__init__()
        self.ACCESS_TOKEN = ACCESS_TOKEN
        self.GitVar = Github(self.ACCESS_TOKEN)
        self.METAMODEL_PATH_FILE = ""
        #self.Selected_item_in_tree_view = ""


    # def loginGitHub(self):
    #     #connect to github
    #     #ACCESS_TOKEN = "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"
       
    #     self.GitVar = Github(self.ACCESS_TOKEN)
       
    #     check_username = self.GitVar.get_user()
    #    # print(check_username)
    #    # print(check_username.login)
    #     return True
    #     # if check_username == self.USERNAME:
    #     #     print("login")
    #     #     return True
    #     # else:
    #     #     print("Nooooo")
    #     #     return False

    # def getSelected_item_in_tree_view(self):
    #     return self.Selected_item_in_tree_view
    # def setSelected_item_in_tree_view(self, item):
    #     self.Selected_item_in_tree_view = item

    def load_users_from_github(self):
        GITHUB_TOKEN = "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"
        REPO_OWNER = "sajadkasaei"
        REPO_NAME = "Braverge-Tool"
        FILE_PATH = "user/users.json"
        BRANCH = "main"

        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")

        try:
            file = repo.get_contents(FILE_PATH, ref=BRANCH)
            content = file.decoded_content.decode("utf-8")
            users = json.loads(content)
            return users, file.sha
        except Exception:
            return {}, None
    
    def load_user_tokens(self, username):
        users, _ = self.load_users_from_github()
        if username in users:
            return users[username].get("tokens", [])
        return []
    
    

    





    def getMETAMODEL_PATH_FILE(self):
        return self.METAMODEL_PATH_FILE
    def setMETAMODEL_PATH_FILE(self, pathFile):
        self.METAMODEL_PATH_FILE = pathFile


    def getACCESS_TOKEN(self):
        return self.ACCESS_TOKEN
    def loginGitHubACCESS_TOKEN(self):
        self.GitVar = Github(self.ACCESS_TOKEN)
        return self.GitVar


# #connect to github
# ACCESS_TOKEN = "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"
# g = Github(ACCESS_TOKEN)
# print(g.get_user().login)

    def uploadFile(self, filePath, filename, fileDir , myRepo):
        #accsess to the repository
        repo = self.GitVar.get_user().get_repo(myRepo)
        all_files = []
        contents = repo.get_contents("") #get contents of the repository
        
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                file = file_content
                all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))
        
        #create object
        self.myBloom_Object = myBloom(self.getMETAMODEL_PATH_FILE())
        self.myBloom_Object.create_UUID_For_All_Elements(filePath)

        with open(filePath, 'r') as file:
            content = file.read()
        # Upload to github
        git_prefix = fileDir  #'folder1/'
        git_file = git_prefix + filename
        git_branch_info_file = git_file.replace('.xmi', 'Branch_Info.json')
        if git_file in all_files:
            contents = repo.get_contents(git_file)
            content_branchinfo = repo.get_contents(git_branch_info_file)

            #
            #create BLOOM
            #
            mydata = contents.decoded_content
            data_branchinfo = content_branchinfo.decoded_content
            #Writing path

            server_last_version= "server_last_version.xmi"
            metaModel = self.getMETAMODEL_PATH_FILE()   #"C:/Users/Admin/Desktop/VSM/simpleOO.ecore"                           ########define meta model

            with open(filePath.replace(filename, '')+server_last_version, 'wb') as f:
                f.write(mydata)
            with open(filePath.replace(filename,'Branch_Info.json'), 'wb') as f:
                f.write(data_branchinfo)
            
            self.myBloom_Object.compare_two_models_UUID(metaModel, filePath.replace(filename, '')+"server_last_version.xmi", filePath, filePath.replace(filename, ''))

            with open(filePath.replace(filename, '') + 'Version_Info.json', 'r') as jfile:
                dataJson = json.load(jfile)
            jfile.close()
            # Serializing json
            dataJson = json.dumps(dataJson, indent=4)
            
            version_ID = str(uuid.uuid4().hex)

            repo.create_file(git_prefix + version_ID + "Version_Info.json", "committing Version Info file", dataJson, branch="main")
            # print(git_prefix + version_ID + 'Version Info CREATED')
           
            repo.update_file(contents.path, "committing files", content, contents.sha, branch="main")
            # print(git_file + ' UPDATED')
            
            with open(filePath.replace(filename,'Branch_Info.json'), 'r') as jfile:
                dataJson = json.load(jfile)
                #dataJson['Versions_ID'].append({ len(dataJson['Versions_ID']) : version_ID})       ##################
                dataJson['Versions_ID'].append(version_ID)
            
            with open(filePath.replace(filename,'Branch_Info.json'), 'w') as file:
                json.dump(dataJson, file)
            with open(filePath.replace(filename,'Branch_Info.json'), 'r') as sjfile:
                filecontent_Json_branch_Info = json.load(sjfile)
            sjfile.close()
            dataJsonfilecontent_Json_branch_Info = json.dumps(filecontent_Json_branch_Info, indent=4)
            
            conJsonInfo = repo.get_contents(git_prefix+ filename.replace('.xmi','Branch_Info.json'))
            repo.update_file(conJsonInfo.path, "committing files", dataJsonfilecontent_Json_branch_Info, conJsonInfo.sha, branch="main")

        else:
            print("ERROR: Project Does NOT Exist")
            #create versions history
            # G=nx.Graph()
            # G.add_node("end")
            # G.add_node("currentVersion")
            # G.add_edge("end" , "currentVersion")
            # nx.write_adjlist(G, filePath.replace(filename,'') + "versions_History.adjlist")
            # with open(filePath.replace(filename,'') + "versions_History.adjlist", 'r') as file:
            #     contentVersion_History = file.read()
            # repo.create_file(git_prefix+"versions_History.adjlist", "committing files", contentVersion_History, branch="main")

            # nx.draw(G,with_labels = True)
            # plt.show()########

            # repo.create_file(git_file, "committing files", content, branch="main")
            # print(git_file + ' CREATED')

            # branch_ID = str(uuid.uuid4().hex)
            # branch_info = {'branch_ID': branch_ID,
            #                     'pivot_ID': branch_ID,
            #                     'access_control': 'public',
            #                     'branch_Pattern': 'long',
            #                     'branch_Strategy': 'full'}
            # # Serializing json
            # json_branch_info = json.dumps(branch_info, indent=4)
            # # Writing to sample.json
            # with open(filePath.replace(filename,'') + branch_ID + "Branch_Info.json", "w") as outfile:
            #     outfile.write(json_branch_info)
            # outfile.close()

            # repo.create_file( git_prefix + branch_ID + "Branch_Info.json", "committing files", json_branch_info, branch="main")
            


    def downloadFile(self, myWorkSpace, myFile, myRepo, parentFolder):
        #accsess to the repository
        repo = self.GitVar.get_user().get_repo(myRepo)
        parentFolder = str(parentFolder).replace('/','')
        contents = repo.get_contents(parentFolder+ myFile)
        mydata = contents.decoded_content
        #decoded = base64.decodebytes(mydata)
       # path = dirPath

       #Writing path
        with open(myWorkSpace+ myFile, 'wb') as f:
            f.write(mydata)

    def downloadFile_fromGitHub(self, myWorkSpace, myFile, myRepo, parentFolder, nameWritten):
        #accsess to the repository
        repo = self.GitVar.get_user().get_repo(myRepo)
        parentFolder = str(parentFolder).replace('/','')
        contents = repo.get_contents(parentFolder+ myFile)
        mydata = contents.decoded_content
        #decoded = base64.decodebytes(mydata)
       # path = dirPath
        
       #Writing path
        with open(myWorkSpace+ nameWritten, 'wb') as f:
            f.write(mydata)

    def getRepos(self):
        return self.GitVar.get_user().get_repos() #myRepos
    
    def getRepos_contents(self, repoName, folderName):
       #accsess to the repository
        folderName = str(folderName).replace('/','')
        repo = self.GitVar.get_user().get_repo(repoName)
        all_dir = []
        all_files = []
        try:
            contents = repo.get_contents(folderName) #get contents of the repository
        except:
            print("Please create project!")
            contents = None
        return contents


    def create_previous_version(self, filePath, selectedModelFile, lastModelFile):

        self.myBloom_Object = myBloom(self.getMETAMODEL_PATH_FILE())
        self.myBloom_Object.Bloom_create_previous_version(filePath, selectedModelFile, lastModelFile)

    def create_new_project_modeling(self, filePath, filename, fileDir , myRepo, username):
                    #accsess to the repository
                    #filename is the name of the selected file
        repo = self.GitVar.get_user().get_repo(myRepo)
        all_files = []
        contents = repo.get_contents("") #get contents of the repository
        
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                file = file_content
                all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))
        #create object
        self.myBloom_Object = myBloom(self.getMETAMODEL_PATH_FILE())
        self.myBloom_Object.create_UUID_For_All_Elements(filePath)
        with open(filePath, 'r') as file:
            content = file.read()
        # Upload to github
        git_prefix = fileDir  #'folder1/'
        branch_ID = str(uuid.uuid4().hex)
    
        git_file = git_prefix + branch_ID + ".xmi"#+ filename

        branch_ID_Local = str(uuid.uuid4().hex)
        git_file_Local = git_prefix + branch_ID_Local + ".xmi"#+ filename

        if git_file in all_files or git_prefix + filename in all_files:
            print("ERROR: PROJECT EXISTS")
        else:
            # #create versions history JASON ##################


            # #create versions history
            # G=nx.Graph()
            # G.add_node("end")
            # G.add_node("currentVersion")
            # G.add_edge("end" , "currentVersion")
            # nx.write_adjlist(G, filePath.replace(filename,'') + "versions_History.adjlist")
            # with open(filePath.replace(filename,'') + "versions_History.adjlist", 'r') as file:
            #     contentVersion_History = file.read()
            # repo.create_file(git_prefix+ branch_ID + "_versions_History.adjlist", "committing files", contentVersion_History, branch="main")

            # nx.draw(G,with_labels = True)
            # plt.show()########

            repo.create_file(git_file, "committing files", content, branch="main")
            print(git_file + ' CREATED')

            branch_info = {'branch_ID': branch_ID,
                                'pivot_ID': branch_ID,
                                'collaborators': 'public',
                                'branch_Pattern': 'long',
                                'branch_Scope': 'full',
                                'Versions_ID' : [branch_ID]}
            # Serializing json
            json_branch_info = json.dumps(branch_info, indent=4)
            # Writing to sample.json
            with open(filePath.replace(filename,'') + "Branch_Info.json", "w") as outfile:
                outfile.write(json_branch_info)
            outfile.close()

            repo.create_file( git_prefix + branch_ID + "Branch_Info.json", "committing files", json_branch_info, branch="main")

            ## for current user we create a branch on the local
            
            branch_info_local = {'branch_ID': branch_ID_Local,
                                'pivot_ID': branch_ID,
                                'collaborators': username,
                                'branch_Pattern': 'short',
                                'branch_Scope': 'full',
                                'Versions_ID' : [branch_ID_Local]}
            # Serializing json
            json_branch_info_local = json.dumps(branch_info_local, indent=4)
            # Writing to sample.json
            with open(filePath.replace(filename,'') + "Branch_Info.json", "w") as outfile:
                outfile.write(json_branch_info_local)
            outfile.close()

            repo.create_file( git_prefix + branch_ID_Local + "Branch_Info.json", "committing files", json_branch_info_local, branch="main")
            repo.create_file( git_file_Local, "committing files", content, branch="main")
            os.rename(filePath, filePath.replace(filename, branch_ID_Local + ".xmi")) #+ filename))
            
    def delete_branch(self, fileDir, repoFil, listFiles):
        repo = self.GitVar.get_user().get_repo(repoFil)

        for file_name in listFiles:
            file_path = fileDir + file_name  # full path in repo
            try:
                content = repo.get_contents(file_path, ref="main")  # get SHA
                repo.delete_file(
                    path=file_path,
                    message=f"Deleting {file_name}",
                    sha=content.sha,
                    branch="main"
                )
            except GithubException as e:
                if e.status == 404:
                    print(f"File not found: {file_path}")
                else:
                    raise
    
    def update_branch_metadata(self, filePath, fileDir, repoFil, branch_ID_Local, branch_ID, username, branch_Pattern, branch_Scope, Versions_ID):
        branch_info_local = {'branch_ID': branch_ID_Local,
                                'pivot_ID': branch_ID,
                                'collaborators': username,
                                'branch_Pattern': branch_Pattern,
                                'branch_Scope': branch_Scope,
                                'Versions_ID' : Versions_ID}
        
        repo = self.GitVar.get_user().get_repo(repoFil)
        # Serializing json
        json_branch_info_local = json.dumps(branch_info_local, indent=4)
        # Writing to sample.json
        with open(filePath + "Branch_Info.json", "w") as outfile:
            outfile.write(json_branch_info_local)
        outfile.close()
        
        contents = repo.get_contents(fileDir + branch_ID_Local + "Branch_Info.json", ref="main")
        repo.update_file(
            path=contents.path,
            message="Updating Branch_Info.json",
            content=json_branch_info_local,
            sha=contents.sha,
            branch="main"
        )

        

    def create_new__short_branch(self, filePath, filename, fileDir, branch_ID, repoFil, username):

        branch_ID_Local = str(uuid.uuid4().hex)

        repo = self.GitVar.get_user().get_repo(repoFil)

        branch_info_local = {'branch_ID': branch_ID_Local,
                                'pivot_ID': branch_ID,
                                'collaborators': username,
                                'branch_Pattern': 'short',
                                'branch_Scope': 'full',
                                'Versions_ID' : [branch_ID_Local]}
        
        # Serializing json
        json_branch_info_local = json.dumps(branch_info_local, indent=4)
        # Writing to sample.json
        with open(filePath + "Branch_Info.json", "w") as outfile:
            outfile.write(json_branch_info_local)
        outfile.close()
        
        repo.create_file( fileDir + branch_ID_Local + "Branch_Info.json", "committing files", json_branch_info_local, branch="main")
        os.rename(filePath + branch_ID + ".xmi", filePath + branch_ID_Local + ".xmi")
        
        with open(filePath + branch_ID_Local + ".xmi", 'r') as file:
            content = file.read()
        repo.create_file( fileDir + branch_ID_Local + ".xmi", "committing files", content, branch="main")

    ##
    ####### MERGING
    ##
    def GitHub_Merge_Models(self, filePath, metamodelPath, Conflict_Decision = None, Conflict_Decision_Keep_list = None):
        self.myBloom_Object = myBloom(self.getMETAMODEL_PATH_FILE())
        ###
        ## Left = current branch
        ## Right = last model in the pivot branch
        # base = pivot model
        # target = merged model

        #self.myBloom_Object.Three_Way_Merging(filePath, metamodelPath,  "Left.xmi", "Right.xmi", "Base.xmi", "Target.xmi")
        ## priority => Delete > Right Version > Left Version ... Add all elements
        self.myBloom_Object.Three_Way_Merging_Compare_UUID(filePath, metamodelPath,  "Left.xmi", "Right.xmi", "Base.xmi", "Target.xmi", Conflict_Decision, Conflict_Decision_Keep_list)
        
    def set_UUID_Model_Path(self, filePath, modelfile):
        self.myBloom_Object = myBloom(self.getMETAMODEL_PATH_FILE())
        self.myBloom_Object.create_UUID_For_All_Elements(modelfile)
    
    def GitHub_View_Management_AI(self, fileName, path, UserRequest_Input):

        self.myBloom_Object = myBloom(self.getMETAMODEL_PATH_FILE())
        myMeta = self.myBloom_Object.importMetaModel(self.getMETAMODEL_PATH_FILE())
        myModel= self.myBloom_Object.importModel(path + fileName, myMeta)

        mm_root= self.myBloom_Object.importMeta_mm_root(self.getMETAMODEL_PATH_FILE())

        viewObject = ViewManagement()

        Gemini_task = "Gemini task: Based on the user request and the available meta-model elements, determine which type(s) of element the user is referring to."
        Gemini_Instructions = "Instructions: Only return the relevant type(s) from the list above, separated by - with no spaces or line breaks. If no relevant element type can be identified, return only: NONE."

        viewmodel = viewObject.view_generation_AI(myModel, mm_root, UserRequest_Input, Gemini_task, Gemini_Instructions)

        self.myBloom_Object.saveModel( path + '/' + 'viewGemini.xmi', viewmodel[0])

        #creating meta model of the view
        #viewType = viewObject.viewType_generation(mm_root, viewmodel[1])
        #self.myBloom_Object.saveMetaModel( path + '/' + 'viewType.ecore', viewType)

        return True

    def GitHub_View_Management_ItemSelection(self, fileName, path, pathmetamodel, Selected_Repository_name, fileDirP, MetaSelectedItemsList):

        Json_branchInfo_file = ""
        workSpacePath= path + '/'
        self.repoContents = self.getRepos_contents(Selected_Repository_name, fileDirP)
        while self.repoContents:
            oneItem = self.repoContents.pop(0)
            if "Branch_Info" in oneItem.name:
                Json_branchInfo_file = json.loads(oneItem.decoded_content)
                if fileName in Json_branchInfo_file['Versions_ID']:
                    Lastversion_in_branch = Json_branchInfo_file['branch_ID'] + ".xmi"
                    #accsess to the repository
                    myFile = '/' + Json_branchInfo_file['branch_ID'] + ".xmi"
                    self.downloadFile_fromGitHub(workSpacePath , myFile, Selected_Repository_name, fileDirP, Lastversion_in_branch)


        self.myBloom_Object = myBloom(self.getMETAMODEL_PATH_FILE())
        myMeta = self.myBloom_Object.importMetaModel(self.getMETAMODEL_PATH_FILE())
        myModel= self.myBloom_Object.importModel(path + myFile, myMeta)

        mm_root = self.myBloom_Object.importMeta_mm_root(self.getMETAMODEL_PATH_FILE())


        # selectedItem = []
        # for i in range(MetaSelectedItemsList.count()):
        #     item = MetaSelectedItemsList.item(i)
        #     selectedItem.append(item.text())

        viewObject = ViewManagement()
        viewmodel = viewObject.view_generation_SelectedItem(myModel, mm_root, MetaSelectedItemsList)
        

        self.myBloom_Object.saveModel( path + '/' + 'viewSelectedItem.xmi', viewmodel)

        #### creating meta model of the view

        #viewType = viewObject.viewType_generation(mm_root, selectedItem)
        #self.myBloom_Object.saveMetaModel( path + '/' + 'viewType.ecore', viewType)



