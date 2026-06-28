from pyecore.resources import ResourceSet, URI
from pyecore.utils import dispatch
from pyecore.resources.xmi import XMIResource

import networkx as nx #creating graph
import matplotlib.pyplot as plt #drawing graph
import community

import os
import openai
from openai import OpenAI

from google import genai
import re


class ViewManagement():
    
    def __init__(self):
        super().__init__()
        self.user_request = ""
        self.user_prompt = ""
        #apikey Gemini
        self.myGEMINIkey = "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"
        self.Geminitask = ""
        self.GeminiInstructions = ""

    def set_user_view_elementType_selection(self, metaType, metaElList_Json):
        #for x in list_GeminiRes:
            for y in metaElList_Json:
                if metaType == y['element']:
                    y['selection'] = 'True'
                    break
            return metaElList_Json

    def set_user_request(self, userReq):
        self.user_request = userReq
        return True
    
    def get_user_request(self):
        if self.user_request != "":
            return self.user_request
        else:
            return False
    
    def set_user_prompt(self, userPrompt):
        self.user_prompt = userPrompt
        return True
    
    def get_user_prompt(self):
        if self.user_prompt != "":
            return self.user_prompt
        else:
            return False
    
    def set_Gemini_task(self, task):
        self.Geminitask = task
        return True
    
    def get_Gemini_task(self):
        if self.Geminitask != "":
            return self.Geminitask
        else:
            return False
    
    def set_user_instructions(self, instructions):
        self.GeminiInstructions = instructions
        return True
    
    def get_user_instructions(self):
        if self.GeminiInstructions != "":
            return self.GeminiInstructions
        else:
            return False
    
    def gemini_execute(self):
        client = genai.Client(api_key = self.myGEMINIkey)
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=self.get_user_prompt()
        )
        GeminiResponse = response.text
        return GeminiResponse
        
    def Decomposer_Metamodel_NAME(self, myMetamodelPath):
        rset = ResourceSet()
        resource = rset.get_resource(URI(myMetamodelPath))
        mm_root = resource.contents[0]
        rset.metamodel_registry[mm_root.nsURI] = mm_root
        # At this point, the .ecore is loaded in the 'rset' as a metamodel

        myMeta = mm_root

        MetaModel_element_string = ""
        metaElList = []
        for objRef in myMeta.eAllContents():

            if objRef.name != None:

                if MetaModel_element_string == "":
                    MetaModel_element_string = str(objRef.name)
                else:
                    MetaModel_element_string = MetaModel_element_string + ", " + str(objRef.name)

                metaEl = {'element': str(objRef.name) ,
                                                'selection': "false",
                                                #'upperbound': '5',
                                                #'lowerbound': '1',
                                                'value': None}
                metaElList.append(metaEl)
        
        return metaElList, MetaModel_element_string
    
    def Decomposer_Metamodel_byName(self, myMeta):
        MetaModel_element_string = ""
        metaElList = []
        for objRef in myMeta.eAllContents():

            if objRef.name != None:

                if MetaModel_element_string == "":
                    MetaModel_element_string = str(objRef.name)
                else:
                    MetaModel_element_string = MetaModel_element_string + ", " + str(objRef.name)

                metaEl = {'element': str(objRef.name) ,
                                                'selection': "false",
                                                #'upperbound': '5',
                                                #'lowerbound': '1',
                                                'value': None}
                metaElList.append(metaEl)
        
        return metaElList, MetaModel_element_string

    def view_generation_AI(self, myModel, myMetamodel, userRequestElement , GeminiTask, GeminiInstructions):
        
        mm_root = myMetamodel
        model_root = myModel

        decom_Meta = self.Decomposer_Metamodel_byName(mm_root)
        MetaModel_element_string = decom_Meta[1]
        metaElList = decom_Meta[0]

        self.set_Gemini_task(GeminiTask)
        self.set_user_instructions(GeminiInstructions)

        Gemini_task = self.get_Gemini_task() #"Gemini task: Based on the user request and the available meta-model elements, determine which type(s) of element the user is referring to."
        Gemini_Instructions = self.get_user_instructions() #"Instructions: Only return the relevant type(s) from the list above, separated by - with no spaces or line breaks. If no relevant element type can be identified, return only: NONE."
        
        self.set_user_prompt("Context: EMF meta-model with" + MetaModel_element_string + "User request:" + userRequestElement + Gemini_task + Gemini_Instructions)
        
        GeminiRes = self.gemini_execute()

        if GeminiRes.find("NONE") == -1:
            GeminiRes = GeminiRes.split('-')

            listt = []
            for item in GeminiRes:
                listt.append(item)

            listTypeElementMetamodel = []

            for x in listt:
                for y in metaElList:
                    if x == y['element']:
                        y['selection'] = 'True'
                        listTypeElementMetamodel.append(y['element'])

            # Create path to root
            countList = 0
            while countList < len(metaElList):
                mm = metaElList[countList]
                restarted = False  # Flag to check if we restarted

                if mm['selection'] == 'True':
                    for ll in model_root.eAllContents():
                        if mm['element'] == ll.eClass.name:
                            if ll.eContainer().eClass.name not in listTypeElementMetamodel:
                                
                                listTypeElementMetamodel.append(ll.eContainer().eClass.name)
                                metaElList = self.set_user_view_elementType_selection(ll.eContainer().eClass.name, metaElList)
                                countList = 0
                                restarted = True  # mark restart
                                break  # break out of for loop to restart while loop

                if not restarted:
                    countList += 1

            for mm in metaElList:
                for ll in model_root.eAllContents():
                    if mm['selection'] == 'false':
                        if mm['element'] == ll.eClass.name:
                            ll.delete()

        else:
            print("NONE - > View Generation")
            return False
        
        return model_root, listTypeElementMetamodel
            

    
    def view_generation_SelectedItem(self, myModel, myMetamodel, itemList):

        mm_root = myMetamodel
        model_root = myModel
        decom_Meta = self.Decomposer_Metamodel_byName(mm_root)
        metaElList = decom_Meta[0]

        for x in itemList:
            for y in metaElList:
                if x == y['element']:
                    y['selection'] = 'True'

        # Create path to root
        countList = 0
        while countList < len(metaElList):
            mm = metaElList[countList]
            restarted = False  # Flag to check if we restarted

            if mm['selection'] == 'True':
                for ll in model_root.eAllContents():
                    if mm['element'] == ll.eClass.name:
                        if ll.eContainer().eClass.name not in itemList:
                            
                            itemList.append(ll.eContainer().eClass.name)
                            metaElList = self.set_user_view_elementType_selection(ll.eContainer().eClass.name, metaElList)
                            countList = 0
                            restarted = True  # mark restart
                            break  # break out of for loop to restart while loop

            if not restarted:
                countList += 1

        for mm in metaElList:
            for ll in model_root.eAllContents():
                if mm['selection'] == 'false':
                    if mm['element'] == ll.eClass.name:
                        ll.delete()

        return model_root
    
    def viewType_generation(self, myMetamodel, itemList):

        mm_root = myMetamodel

        decom_Meta = self.Decomposer_Metamodel_NAME(mm_root)
        metaElList = decom_Meta[0]

        for x in itemList:
            for y in metaElList:
                if x == y['element']:
                    y['selection'] = 'True'

        # Create path to root
        countList = 0
        while countList < len(metaElList):
            mm = metaElList[countList]
            restarted = False  # Flag to check if we restarted

            if mm['selection'] == 'True':
                for ll in mm_root.eAllContents():
                    if mm['element'] == ll.name:
                        if ll.eContainer().name not in itemList:
                            
                            itemList.append(ll.eContainer().name)
                            metaElList = self.set_user_view_elementType_selection(ll.eContainer().name, metaElList)
                            countList = 0
                            restarted = True  # mark restart
                            break  # break out of for loop to restart while loop

                    if mm['element'] == ll.name:            
                        for M2set in ll._isset:
                            if(M2set.eClass.name == "EReference"):
                                if (type(ll.eGet(M2set.name)).__name__ == "EOrderedSet") or (type(ll.eGet(M2set.name)).__name__ == "ESet"):
                                    for i in ll.eGet(M2set.name):
                                        if i.name not in itemList:
                                            itemList.append(i.name)
                                            metaElList = self.set_user_view_elementType_selection(i.name, metaElList)
                                            countList = 0
                                            restarted = True  # mark restart
                                            break  # break out of for loop to restart while loop
                                else:
                                    print(ll.eGet(M2set.name))
                                    print(ll.eGet(M2set.name).name)
                                    if ll.eGet(M2set.name).name not in itemList:
                                        itemList.append(ll.eGet(M2set.name).name)
                                        metaElList = self.set_user_view_elementType_selection(ll.eGet(M2set.name).name, metaElList)
                                        countList = 0
                                        restarted = True  # mark restart
                                        break  # break out of for loop to restart while loop

            if not restarted:
                countList += 1

        for mm in metaElList:
            for ll in mm_root.eAllContents():
                if mm['selection'] == 'false':
                    if mm['element'] == ll.name:
                        ll.delete()

        return mm_root


    def ask_Gemini_conflict_explanation(self,JsonELEMENTS):
        Gemini_task = "Gemini task: Based on the json representation of two EMF elements, explain why these two elements have conflict."
        Gemini_Instructions = "Instructions: Only return the conclution of your observation."
        self.set_user_prompt("Context: EMF model.\nDetected conflict: {JsonELEMENTS}.\n{Gemini_task}\n{Gemini_Instructions}")
        GeminiRes = self.gemini_execute()
        return GeminiRes