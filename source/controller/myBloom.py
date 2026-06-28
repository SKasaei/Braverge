from rbloom import Bloom
from hashlib import sha256
from pickle import dumps

from pyecore.resources import ResourceSet, URI
from pyecore.utils import dispatch
from pyecore.ecore import EcoreUtils

from pyecore.resources.xmi import XMIResource
from pyecore.ecore import EClass, EAttribute, EString, EObject, EPackage, EReference
from pyecore.ecore import EOrderedSet, ESet

from datetime import datetime
import networkx as nx #creating graph
import matplotlib.pyplot as plt #drawing graph
import community
import uuid # to create uuid
from pyecore.commands import Set, Add, Move

import hashlib
import json

from controller.hashT import HashTable

class myBloom():
    def __init__(self, METAMODEL_FILE_PATH):
        super().__init__()
        #print(METAMODEL_FILE_PATH)
        self.MY_METAMODEL_FILE_PATH = METAMODEL_FILE_PATH
        self.Version_Left = None
        self.Version_Right = None
        self.Version_Base = None
        self.Version_Merged =None

        self.CONFLICT_DELETE_UPDATE = None
        self.CONFLICT_DELETE_USE_OLD = None
        self.CONFLICT_DELETE_MOVE = None
        self.CONFLICT_DELETE_ADD = None
        self.CONFLICT_UPDATE_UPDATE = None
        self.CONFLICT_MOVE_MOVE = None
        self.CONFLICT_INSERT_INSERT = None


    def hash_func(self, obj):
        h = sha256(dumps(obj)).digest()
        return int.from_bytes(h[:16], "big") - 2**127

    def importMetaModel(self, MMPath):
        rset = ResourceSet()
        resource = rset.get_resource(URI(MMPath))
        resource.readonly = False
        mm_root = resource.contents[0]
        rset.metamodel_registry[mm_root.nsURI] = mm_root
        # At this point, the .ecore is loaded in the 'rset' as a metamodel
        return rset
    
    def importMeta_mm_root(self, MMPath):
        rset = ResourceSet()
        resource = rset.get_resource(URI(MMPath))
        resource.readonly = False
        mm_root = resource.contents[0]
        return mm_root

    def importModel(self, MPath,MetaModel):
        resource = MetaModel.get_resource(URI(MPath))
        resource.readonly = False
        model_root = resource.contents[0]
        # At this point, the model instance is loaded!
        for obj1 in model_root.eAllContents():
             if (obj1._internal_id == None):
                  obj1.eSet('_internal_id' , str(uuid.uuid4().hex))
             
        return model_root
    
    def saveModel(self, modelPath, model):
         # SAVE MY view
        resourceSave = XMIResource(URI(modelPath))
        resourceSave.use_uuid = True
        resourceSave.append(model)  # We add the root to the resource
        resourceSave.save()  # will save the result in 'my/path.xmi'
        resourceSave.save(output=URI(modelPath))  # save the result in 'test/path.xmi'

    def saveMetaModel(self, metamodelPath, meta):
         ## SAVING META MODEL (.ecore file)
        rset = ResourceSet()
        resource = rset.create_resource(URI(metamodelPath))
        resource.append(meta)
        resource.save()
        resource.save(output=URI(metamodelPath))
    
    def compare_two_models_UUID(self, MyMetaModel_path, MyModel_V1, MyModel_V2, Path):
        MyMetaModel = self.importMetaModel(MyMetaModel_path)
        version1 = self.importModel(MyModel_V1, MyMetaModel)
        version2 = self.importModel(MyModel_V2, MyMetaModel)

        open(Path + 'temp.xmi', 'w').close()
        list_obj = []
        
        Check_Deleted_Elements = True
        Check_Added_Elements = True

        open(Path + 'temp.xmi', 'w').close()
        #Updetated_Det=""
        UpFlag = 0
        upElements = []
        addElements = []
        delElements = []
        
        #finding added elements     
          
        for obj2 in version2.eAllContents():
            for obj1 in version1.eAllContents():
                if (obj2.eGet('_internal_id') == obj1.eGet('_internal_id')):
                    Check_Added_Elements = False
                    break

            if (Check_Added_Elements == True):
                addElements.append({'operation': 'ADD', 'internal_id': obj2.eGet('_internal_id')})

            Check_Added_Elements = True

        for obj1 in version1.eAllContents():

            for obj2 in version2.eAllContents():

                # finding changes in properties - it means that an element is updated!
                # common isSet between two version, ADD isSet in version 2, DEL isSet in version 1 ############ %%%%%%% #########
                
                # finding two similar elements
                if ( obj1.eGet('_internal_id') == obj2.eGet('_internal_id') ):

                    Check_Deleted_Elements = False
                    
                    # for properties are set in the version 2
                    for M2set in obj2._isset:

                        # if this property is set in version 1
                        if ( (M2set in obj1._isset) ):
                            
                            # property could be EReference OR static value (other)
                            if(M2set.eClass.name == "EReference"):

                                # EReference: EOrderedSet (list of ...) OR SINGLE
                                if (type(obj2.eGet(M2set.name)).__name__ == "EOrderedSet") or (type(obj2.eGet(M2set.name)).__name__ == "ESet"):
                                    #Updetated_Det = ""
                                    setEl_in_objHT = []
                                    for elInOs in obj1.eGet(M2set.name):
                                        setEl_in_objHT.append(elInOs.eGet('_internal_id'))

                                    setEl_in_objM2 = []
                                    for elInOss in obj2.eGet(M2set.name):
                                        setEl_in_objM2.append(elInOss.eGet('_internal_id'))

                                    if ( set(setEl_in_objM2) != set(setEl_in_objHT) ):
                                        if setEl_in_objM2:
                                            upElement_Json = {'operation': 'ADD', 'type': 'EReference', 'internal_id': obj2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': setEl_in_objM2}
                                            upElements.append(upElement_Json)

                                        if setEl_in_objHT:
                                            upElement_Json = {'operation': 'DEL', 'type': 'EReference', 'internal_id': obj2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': setEl_in_objHT}
                                            upElements.append(upElement_Json)

                                    
                                        ## ## ##
                                    # for oneSet in obj2.eGet(M2set.name):
                                    #     if ( ( oneSet.eGet('_internal_id') not in setEl_in_objHT) ):
                                    #         #
                                    #         #Updetated_Det = "ADD " + obj2.eGet('_internal_id') + "=" + M2set.name + "!"  + oneSet.eGet('_internal_id') + "\n"
                                    #         upElement_Json = {'operation': 'ADD', 'type': 'EReference', 'internal_id': obj2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': oneSet.eGet('_internal_id')}
                                    #         upElements.append(upElement_Json)

                                    # for oneSetHT in obj1.eGet(M2set.name):
                                    #     if ( ( oneSetHT.eGet('_internal_id') not in setEl_in_objM2) ):
                                    #         #
                                    #         #Updetated_Det = "DEL " + obj2.eGet('_internal_id') + "=" + M2set.name + "!"  + oneSetHT.eGet('_internal_id') + "\n"
                                    #         upElement_Json = {'operation': 'DEL', 'type': 'EReference', 'internal_id': obj2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': oneSetHT.eGet('_internal_id')}
                                    #         upElements.append(upElement_Json)
                                    
                                else:
                                    
                                    if ( ( obj2.eGet(M2set.name).eGet('_internal_id') != obj1.eGet(M2set.name).eGet('_internal_id') ) ):
                                        #Updetated_Det = "ADD " + obj2.eGet('_internal_id') + "=" + M2set.name + "!" + obj2.eGet(M2set.name).eGet('_internal_id') + "\n"
                                        #Updetated_Det = Updetated_Det + "DEL " + obj2.eGet('_internal_id') + "=" + M2set.name + "!" + obj1.eGet(M2set.name).eGet('_internal_id')
                                        if ( obj1.eContainer().eGet('_internal_id') != obj2.eContainer().eGet('_internal_id') ):
                                            upElement_Json = {'operation': 'ADD', 'type': 'EContainer', 'internal_id': obj2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': obj2.eGet(M2set.name).eGet('_internal_id')}
                                            upElements.append(upElement_Json)
                                            upElement_Json = {'operation': 'DEL', 'type': 'EContainer', 'internal_id': obj2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': obj1.eGet(M2set.name).eGet('_internal_id')}
                                            upElements.append(upElement_Json)
                                        else:
                                            upElement_Json = {'operation': 'ADD', 'type': 'EReference', 'internal_id': obj2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': obj2.eGet(M2set.name).eGet('_internal_id')}
                                            upElements.append(upElement_Json)
                                            upElement_Json = {'operation': 'DEL', 'type': 'EReference', 'internal_id': obj2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': obj1.eGet(M2set.name).eGet('_internal_id')}
                                            upElements.append(upElement_Json)

                            else:
                                if ( ( obj2.eGet(M2set.name) != obj1.eGet(M2set.name) ) ):
                                    #Updetated_Det = "ADD " + obj2.eGet('_internal_id') + "=" + M2set.name + "!" + obj2.eGet(M2set.name) + "\n"
                                    #Updetated_Det = Updetated_Det + "DEL " + obj2.eGet('_internal_id') + "=" + M2set.name + "!" + obj1.eGet(M2set.name)
                                    upElement_Json = {'operation': 'ADD', 'type': 'other', 'internal_id': obj2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': obj2.eGet(M2set.name) }
                                    upElements.append(upElement_Json)
                                    upElement_Json = {'operation': 'DEL', 'type': 'other', 'internal_id': obj2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': obj1.eGet(M2set.name)}
                                    upElements.append(upElement_Json)
                        

                        # if this property is not set in the version 1
                        ## it means that null => new value
                        #### in this situation, we do not generate a pair of (delete, add)
                        else: #add new one
                            if(M2set.eClass.name == "EReference"):
                                if (type(obj2.eGet(M2set.name)).__name__ == "EOrderedSet") or (type(obj2.eGet(M2set.name)).__name__ == "ESet"):
                                    #fTemptex = ""
                                    listupItem = []
                                    for oneSet in obj2.eGet(M2set.name):
                                        #
                                        #fTemptex = fTemptex + oneSet.eGet('_internal_id') #+ ","
                                        #Updetated_Det = "ADD " + obj2.eGet('_internal_id') + "=" + M2set.name + "!"  + fTemptex + "\n" ##
                                        listupItem.append(oneSet.eGet('_internal_id'))

                                    if listupItem: #check list not empty
                                        upElement_Json = {'operation': 'ADD', 'type': 'EReference', 'internal_id': obj2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': listupItem }
                                        upElements.append(upElement_Json)
                                    
                                else:
                                        if ( obj1.eContainer().eGet('_internal_id') != obj2.eContainer().eGet('_internal_id') ):
                                            upElement_Json = {'operation': 'ADD', 'type': 'EContainer', 'internal_id': obj2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': obj2.eGet(M2set.name).eGet('_internal_id')  }
                                            upElements.append(upElement_Json)
                                        else:
                                            #
                                            #Updetated_Det = "ADD " + obj2.eGet('_internal_id') + "=" + M2set.name + "!" + obj2.eGet(M2set.name).eGet('_internal_id') 
                                            upElement_Json = {'operation': 'ADD', 'type': 'EReference', 'internal_id': obj2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': obj2.eGet(M2set.name).eGet('_internal_id')  }
                                            upElements.append(upElement_Json)

                            else:
                                    #
                                    #Updetated_Det = "ADD " + obj2.eGet('_internal_id') + "=" + M2set.name + "!" + obj2.eGet(M2set.name) 
                                    upElement_Json = {'operation': 'ADD', 'type': 'other', 'internal_id': obj2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': obj2.eGet(M2set.name)   }
                                    upElements.append(upElement_Json)
                    
                    # for properties are set in the version 1
                    for HTset in obj1._isset:
                        if (HTset not in obj2._isset):
                            if(HTset.eClass.name == "EReference"):
                                if (type(obj1.eGet(HTset.name)).__name__ == "EOrderedSet") or type(obj1.eGet(HTset.name)).__name__ == "ESet"              or (type(obj2.eGet(M2set.name)).__name__ == "ESet"):
                                    #fTemptex = ""
                                    listupItem = []
                                    for oneSet in obj1.eGet(HTset.name):
                                        #
                                        #fTemptex = fTemptex + oneSet.eGet('_internal_id') #+ ","
                                        
                                        #Updetated_Det = "DEL " + obj1.eGet('_internal_id') + "=" + HTset.name + "!"  + fTemptex + "\n" ##
                                        
                                        listupItem.append(oneSet.eGet('_internal_id'))
                                    
                                    if listupItem:
                                        upElement_Json = {'operation': 'DEL', 'type': 'EReference', 'internal_id': obj1.eGet('_internal_id'), 'feature_name': HTset.name, 'feature_value': listupItem   }
                                        upElements.append(upElement_Json)
                                                            
                                else:
                                        if ( obj1.eContainer().eGet('_internal_id') != obj2.eContainer().eGet('_internal_id') ):
                                                #
                                            #Updetated_Det = "DEL " + obj1.eGet('_internal_id') + "=" + HTset.name + "!" + obj1.eGet(HTset.name).eGet('_internal_id') 
                                            upElement_Json = {'operation': 'DEL', 'type': 'EContainer', 'internal_id': obj1.eGet('_internal_id'), 'feature_name': HTset.name, 'feature_value': obj1.eGet(HTset.name).eGet('_internal_id')    }
                                            upElements.append(upElement_Json)
                                        else:
                                            #
                                            #Updetated_Det = "DEL " + obj1.eGet('_internal_id') + "=" + HTset.name + "!" + obj1.eGet(HTset.name).eGet('_internal_id') 
                                            upElement_Json = {'operation': 'DEL', 'type': 'EReference', 'internal_id': obj1.eGet('_internal_id'), 'feature_name': HTset.name, 'feature_value': obj1.eGet(HTset.name).eGet('_internal_id')    }
                                            upElements.append(upElement_Json)

                            else:
                                    #
                                    #Updetated_Det = "DEL " + obj1.eGet('_internal_id') + "=" + HTset.name + "!" + obj1.eGet(HTset.name) 
                                    upElement_Json = {'operation': 'DEL', 'type': 'other', 'internal_id': obj1.eGet('_internal_id'), 'feature_name': HTset.name, 'feature_value': obj1.eGet(HTset.name)    }
                                    upElements.append(upElement_Json)
            
            #finding deleted elements
            if (Check_Deleted_Elements == True):
                container_id = obj1.eContainer().eGet('_internal_id')
                delfetu = self.get_deleted_element_features(obj1)

                resourceSave = XMIResource(URI(Path + 'temp.xmi'))
                resourceSave.use_uuid = True
                resourceSave.append(obj1)
                resourceSave.save()
                resourceSave.save(output=URI(Path + 'temp.xmi'))

                with open(Path + 'temp.xmi', 'r') as file:
                        myFile = file.read()
                file.close()
                
                delElements.append( {'operation': 'DEL', 'internal_id': obj1.eGet('_internal_id'), 'container_id': container_id, 'file_source_xmi': myFile, 'element_References': delfetu[1]} )
                
            Check_Deleted_Elements = True

        
        myDictADD = { "ADD": addElements}              
        myDictUP = { "UPDATE": upElements }  
        myDictDEL = { "DELETE": delElements} 

        my_json_structure = []
        my_json_structure.append(myDictDEL)
        my_json_structure.append(myDictADD)
        my_json_structure.append(myDictUP)

        # Serializing json
        json_object_SAVE = json.dumps(my_json_structure, indent=4)
        
        # Writing to sample.json
        with open(Path + "Version_Info.json", "w") as outfile:
            outfile.write(json_object_SAVE)
        outfile.close()

        return True
    
    def defineBloom(self):      #can set Small, medium, large projects .... for setting elements in blomm
        mybloomFilter = Bloom(100_000, 0.01, self.hash_func)
        return mybloomFilter

    def createBloomVersion(self, MyModel):
        bf= self.defineBloom()
        for obj0 in MyModel.eAllContents():
            bloomKey = obj0.eGet('_internal_id')  #.name + obj0._container.name             #*******eGet('UUID_Versioning_System')
            bf.add(bloomKey)
        return bf
    
    def createBloom_with_path_version(self, MyModel_path, MyMetaModel_path):
        
        MyMetaModel = self.importMetaModel(MyMetaModel_path)
        myModel = self.importModel(MyModel_path, MyMetaModel)
        bf= self.defineBloom()
        for obj0 in myModel.eAllContents():
            bloomKey = obj0.eGet('_internal_id')              #name + obj0._container.name
            bf.add(bloomKey)
        return bf

    def saveBloomFile(self, bloomFile, fileName):
        # saving to a file
        bloomFile.save( fileName )

    # def create_Previous_Version(self, previousBloom):
    #     for obj in MyModel.eAllContents():
    #         bloomKey = obj.name + obj._container.name
    #         if ((bloomKey in previousBloom) == False):
    #             obj.delete() 

    def upload_Bloom_version_file(self, server_last_version, filePath):
        MyMetaModel = self.importMetaModel(self.MY_METAMODEL_FILE_PATH)

        MyModel = self.importModel(filePath + server_last_version, MyMetaModel)

        mybloomfile = self.createBloomVersion(MyModel)
        versionName = uuid.uuid4().hex
        bloomPathFile = filePath+versionName + ".bloom"
        self.saveBloomFile(mybloomfile, bloomPathFile)
        return bloomPathFile, versionName + ".bloom"

    def Bloom_create_previous_version(self, filePath, selectedModelFile, lastModelFile):
        
        Mypath = filePath + "/"
        MyMetaModel = self.importMetaModel(self.MY_METAMODEL_FILE_PATH)
        PathMetaModel = self.MY_METAMODEL_FILE_PATH

        #MyModel = self.importModel(Mypath+'server_last_version.xmi', MyMetaModel)
        MyModel = self.importModel(Mypath+ lastModelFile, MyMetaModel) #current model

        with open(Mypath + 'Version_Info.json', 'r') as jfile:
            dataJson = json.load(jfile)
        jfile.close()

        update_Json = []
        delete_Json = []
        add_Json = []

        for dataJson_item in dataJson:
            if 'UPDATE' in dataJson_item:
                update_Json = dataJson_item['UPDATE']
            if 'DELETE' in dataJson_item:
                delete_Json = dataJson_item['DELETE']
            if 'ADD' in dataJson_item:
                add_Json = dataJson_item['ADD']

        #check empty
       
        
        #print("Remove")
        # if delete_Json:
        #     self.add_elements_TO_current_model(MyModel, MyMetaModel, Mypath, delete_Json)

        #delete_Json = delete_Json.reverse()
        count_Base = 0
        for item in delete_Json:
            if count_Base == 0:
                #MyMetaModel = self.importMetaModel(self.MY_METAMODEL_FILE_PATH)
                #BaseModel = self.importModel(Mypath + BaseVersion, MyMetaModel)
                self.add_elements_TO_model_EVO(MyModel, MyMetaModel, lastModelFile, Mypath, item, update_Json)
                count_Base = 1
            else:
                MyMetaModel = self.importMetaModel(self.MY_METAMODEL_FILE_PATH)
                BaseModel = self.importModel(Mypath + lastModelFile, MyMetaModel)
                MyModel = BaseModel
                self.add_elements_TO_model_EVO(BaseModel, MyMetaModel, lastModelFile, Mypath, item, update_Json)
                
        #print("Add")
        if update_Json:
            self.reverse_updating_elements_model(MyModel, update_Json)
        #print("Update")

        if add_Json:
            self.remove_elements_OF_current_model(MyModel, add_Json)
        
                # SAVE MY MODEL
        resourceSave = XMIResource(URI(Mypath + selectedModelFile))
        resourceSave.use_uuid = True
        resourceSave.append(MyModel)  # We add the root to the resource
        resourceSave.save()  # will save the result in 'my/path.xmi'
        resourceSave.save(output=URI(Mypath + selectedModelFile))  # save the result in 'test/path.xmi'
        #print("....CREATED....")


        #print("========")



    def identify_deleted_elements(self, versionP1, Bloom_version2, metaModel, Path, version2):

        MyMetaModel = self.importMetaModel(metaModel)
        version1 = self.importModel(versionP1, MyMetaModel)
        versionM2 = self.importModel(version2, MyMetaModel)
        
        open(Path + 'temp.xmi', 'w').close()
        
        deleted_elements_Info = "Start_Deleted_Elements_Features_Versioning_System \n"

        list_obj = []
        temp_textFile = ""
        delElements = []

        # Create a hash table with %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
	    # a capacity of 1000
        self.myHashTable_Object = HashTable(1000)

        for obj0 in version1.eAllContents():
            bloomKey00 = obj0.eGet('_internal_id')            #name + obj0._container.name

            if (obj0._container.eGet('_internal_id') not in list_obj):

                if ((bloomKey00 in Bloom_version2) == False):
                    #
                    container_id = obj0.eContainer().eGet('_internal_id')
                    containing_feature = obj0.eContainmentFeature()

                    delfetu = self.get_deleted_element_features(obj0)
                    deleted_elements_Info = deleted_elements_Info + obj0.eGet('_internal_id') + "::" + delfetu[0] + "\n"

                    resourceSave = XMIResource(URI(Path + 'temp.xmi'))
                    resourceSave.use_uuid = True
                    resourceSave.append(obj0)
                    resourceSave.save()
                    resourceSave.save(output=URI(Path + 'temp.xmi'))

                    with open(Path + 'temp.xmi', 'r') as file:
                            myFile = file.read()
                    file.close()
                    
                   
                    #
                    delElements.append( {'operation': 'DEL', 'internal_id': obj0.eGet('_internal_id'), 'container_id': container_id, 'file_source_xmi': myFile, 'element_References': delfetu[1]} )
                    #

                    temp_textFile = temp_textFile + "element" + "\n" + myFile

                    list_obj.append(bloomKey00)

            if ((bloomKey00 in Bloom_version2) == True):
                 self.myHashTable_Object.insert(obj0.eGet('_internal_id'), obj0)

        deleted_elements_Info = deleted_elements_Info + "\n" + "End_Deleted_Elements_Features_Versioning_System \n"
        
        ######################################################## 
        #self.identify_Updated_Elements(self.myHashTable_Object, versionM2)
        updated_elements_Info = "Start_Updated_Elements_Features_Versioning_System"
        open(Path + 'temp.xmi', 'w').close()
        tempUpdate_textFile = ""
        Updetated_Det=""
        UpFlag = 0
        upElements = []
        
        for objM2 in versionM2.eAllContents():

            # common isSet between two version, ADD isSet in version 2, DEL isSet in version 1 ############ %%%%%%% #########

            if ( objM2.eGet('_internal_id') in self.myHashTable_Object ):
                objHT = self.myHashTable_Object.search(objM2.eGet('_internal_id'))
                 
                for M2set in objM2._isset:
                    if ( (M2set in objHT._isset) ):
                        if(M2set.eClass.name == "EReference"):
                            if (type(objM2.eGet(M2set.name)).__name__ == "EOrderedSet") or (type(objM2.eGet(M2set.name)).__name__ == "ESet"):
                                Updetated_Det = ""
                                setEl_in_objHT = []
                                for elInOs in objHT.eGet(M2set.name):
                                     setEl_in_objHT.append(elInOs.eGet('_internal_id'))

                                setEl_in_objM2 = []
                                for elInOss in objM2.eGet(M2set.name):
                                     setEl_in_objM2.append(elInOss.eGet('_internal_id'))
                                     
                                for oneSet in objM2.eGet(M2set.name):
                                    if ( ( oneSet.eGet('_internal_id') not in setEl_in_objHT) ):
                                        #
                                        Updetated_Det = "ADD " + objM2.eGet('_internal_id') + "=" + M2set.name + "!"  + oneSet.eGet('_internal_id') + "\n"
                                        upElement_Json = {'operation': 'ADD', 'type': 'EReference', 'internal_id': objM2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': oneSet.eGet('_internal_id')}
                                        upElements.append(upElement_Json)

                                for oneSetHT in objHT.eGet(M2set.name):
                                    if ( ( oneSetHT.eGet('_internal_id') not in setEl_in_objM2) ):
                                        #
                                        Updetated_Det = "DEL " + objM2.eGet('_internal_id') + "=" + M2set.name + "!"  + oneSetHT.eGet('_internal_id') + "\n"
                                        upElement_Json = {'operation': 'DEL', 'type': 'EReference', 'internal_id': objM2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': oneSetHT.eGet('_internal_id')}
                                        upElements.append(upElement_Json)
                                #
                                tempUpdate_textFile = tempUpdate_textFile + Updetated_Det 
                                
                            else:
                                if ( ( objM2.eGet(M2set.name).eGet('_internal_id') != objHT.eGet(M2set.name).eGet('_internal_id') ) ):
                                    Updetated_Det = "ADD " + objM2.eGet('_internal_id') + "=" + M2set.name + "!" + objM2.eGet(M2set.name).eGet('_internal_id') + "\n"
                                    Updetated_Det = Updetated_Det + "DEL " + objM2.eGet('_internal_id') + "=" + M2set.name + "!" + objHT.eGet(M2set.name).eGet('_internal_id')
                                    #Updetated_Det = "common " + objM2.eGet('_internal_id') + "=" + M2set.name + "!" + objM2.eGet(M2set.name).eGet('_internal_id') + "<-" + objHT.eGet(M2set.name).eGet('_internal_id')
                                    upElement_Json = {'operation': 'ADD', 'type': 'EReference', 'internal_id': objM2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': objM2.eGet(M2set.name).eGet('_internal_id')}
                                    upElements.append(upElement_Json)
                                    upElement_Json = {'operation': 'DEL', 'type': 'EReference', 'internal_id': objM2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': objHT.eGet(M2set.name).eGet('_internal_id')}
                                    upElements.append(upElement_Json)
                                    tempUpdate_textFile = tempUpdate_textFile + Updetated_Det + "\n"

                        else:
                            if ( ( objM2.eGet(M2set.name) != objHT.eGet(M2set.name) ) ):
                                #
                                Updetated_Det = "ADD " + objM2.eGet('_internal_id') + "=" + M2set.name + "!" + objM2.eGet(M2set.name) + "\n"
                                Updetated_Det = Updetated_Det + "DEL " + objM2.eGet('_internal_id') + "=" + M2set.name + "!" + objHT.eGet(M2set.name)
                                #Updetated_Det = "common " + objM2.eGet('_internal_id') + "=" + M2set.name + "!" + objM2.eGet(M2set.name) + "<-" + objHT.eGet(M2set.name)
                                upElement_Json = {'operation': 'ADD', 'type': 'other', 'internal_id': objM2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': objM2.eGet(M2set.name) }
                                upElements.append(upElement_Json)
                                upElement_Json = {'operation': 'DEL', 'type': 'other', 'internal_id': objM2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': objHT.eGet(M2set.name)}
                                upElements.append(upElement_Json)

                                tempUpdate_textFile = tempUpdate_textFile  + Updetated_Det  + "\n"
                    
                    else: #add new one
                        if(M2set.eClass.name == "EReference"):
                            if (type(objM2.eGet(M2set.name)).__name__ == "EOrderedSet") or (type(objM2.eGet(M2set.name)).__name__ == "ESet"):
                                fTemptex = ""
                                listupItem = []
                                for oneSet in objM2.eGet(M2set.name):
                                    #
                                    fTemptex = fTemptex + oneSet.eGet('_internal_id') #+ ","
                                    Updetated_Det = "ADD " + objM2.eGet('_internal_id') + "=" + M2set.name + "!"  + fTemptex + "\n" ##
                                    
                                    listupItem.append(oneSet.eGet('_internal_id'))
                                if listupItem: #check list not empty
                                    upElement_Json = {'operation': 'ADD', 'type': 'EReference', 'internal_id': objM2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': listupItem }
                                    upElements.append(upElement_Json)

                                tempUpdate_textFile = tempUpdate_textFile + Updetated_Det + "\n"
                                
                            else:
                                    #
                                    Updetated_Det = "ADD " + objM2.eGet('_internal_id') + "=" + M2set.name + "!" + objM2.eGet(M2set.name).eGet('_internal_id') 
                                    upElement_Json = {'operation': 'ADD', 'type': 'EReference', 'internal_id': objM2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': objM2.eGet(M2set.name).eGet('_internal_id')  }
                                    upElements.append(upElement_Json)

                                    tempUpdate_textFile = tempUpdate_textFile + Updetated_Det + "\n"

                        else:
                                #
                                Updetated_Det = "ADD " + objM2.eGet('_internal_id') + "=" + M2set.name + "!" + objM2.eGet(M2set.name) 
                                upElement_Json = {'operation': 'ADD', 'type': 'other', 'internal_id': objM2.eGet('_internal_id'), 'feature_name': M2set.name, 'feature_value': objM2.eGet(M2set.name)   }
                                upElements.append(upElement_Json)
                                tempUpdate_textFile = tempUpdate_textFile  + Updetated_Det  + "\n"  
                
                for HTset in objHT._isset:
                    
                    if (HTset not in objM2._isset):
                        
                        if(HTset.eClass.name == "EReference"):
                        
                            if (type(objHT.eGet(HTset.name)).__name__ == "EOrderedSet") or (type(objHT.eGet(M2set.name)).__name__ == "ESet"):
                                
                                fTemptex = ""
                                listupItem = []
                                for oneSet in objHT.eGet(HTset.name):
                                    #
                                    fTemptex = fTemptex + oneSet.eGet('_internal_id') #+ ","
                                    
                                    Updetated_Det = "DEL " + objHT.eGet('_internal_id') + "=" + HTset.name + "!"  + fTemptex + "\n" ##
                                    
                                    listupItem.append(oneSet.eGet('_internal_id'))
                                
                                if listupItem:
                                    upElement_Json = {'operation': 'DEL', 'type': 'EReference', 'internal_id': objHT.eGet('_internal_id'), 'feature_name': HTset.name, 'feature_value': listupItem   }
                                    upElements.append(upElement_Json)
                    
                                tempUpdate_textFile = tempUpdate_textFile + Updetated_Det + "\n"
                                
                            else:
                                    #
                                    Updetated_Det = "DEL " + objHT.eGet('_internal_id') + "=" + HTset.name + "!" + objHT.eGet(HTset.name).eGet('_internal_id') 
                                    upElement_Json = {'operation': 'DEL', 'type': 'EReference', 'internal_id': objHT.eGet('_internal_id'), 'feature_name': HTset.name, 'feature_value': objHT.eGet(HTset.name).eGet('_internal_id')    }
                                    upElements.append(upElement_Json)
                                    tempUpdate_textFile = tempUpdate_textFile + Updetated_Det + "\n"

                        else:
                                #
                                Updetated_Det = "DEL " + objHT.eGet('_internal_id') + "=" + HTset.name + "!" + objHT.eGet(HTset.name) 
                                upElement_Json = {'operation': 'DEL', 'type': 'other', 'internal_id': objHT.eGet('_internal_id'), 'feature_name': HTset.name, 'feature_value': objHT.eGet(HTset.name)    }
                                upElements.append(upElement_Json)
                                tempUpdate_textFile = tempUpdate_textFile  + Updetated_Det  + "\n"  
                             
        myDictUP = { "UPDATE": upElements }  
        myDictDEL = { "DELETE": delElements} 

        my_json_structure = []
        my_json_structure.append(myDictUP)
        my_json_structure.append(myDictDEL)

        # Serializing json
        json_object_SAVE = json.dumps(my_json_structure, indent=4)
        
        # Writing to sample.json
        with open(Path + "Version_Info.json", "w") as outfile:
            outfile.write(json_object_SAVE)
        outfile.close()

        updated_elements_Info = updated_elements_Info + "\n" + tempUpdate_textFile + "End_Updated_Elements_Features_Versioning_System \n"
        ########################################################
        #print(updated_elements_Info)
        
        deleted_elements_Info = updated_elements_Info + deleted_elements_Info
        with open(Path + "Version_Info.txt", 'w') as file:
            file.write(deleted_elements_Info)
        file.close()

        return temp_textFile , Path + "Version_Info.txt"
                

    def identify_deleted_elements_BLOOMFILTER(self, Bloom_version, baseVersionPath , metamodelPath):

        MyMetaModel = self.importMetaModel(metamodelPath)
        baseVersion = self.importModel(baseVersionPath, MyMetaModel)

        deleteElements = []
        for obj0 in baseVersion.eAllContents():
            bloomKey00 = obj0.eGet('_internal_id')         
            if ((bloomKey00 in Bloom_version) == False):
                deleteElements.append(bloomKey00)
        
        return deleteElements 
    
    def identify_added_elements_BLOOMFILTER(self, Bloom_base, VersionLeftPath , VersionRightPath, Path):
        MyMetaModel = self.importMetaModel(self.MY_METAMODEL_FILE_PATH)
        #BaseModel = self.importModel(Path + BaseVersion, MyMetaModel)

        VersionL = self.importModel(VersionLeftPath, MyMetaModel)
        addedElements = []
        for obj1 in VersionL.eAllContents():
            bloomKey00 = obj1.eGet('_internal_id')         
            if ((bloomKey00 in Bloom_base) == False):

                container_id = obj1.eContainer().eGet('_internal_id')
                delfetu = self.get_deleted_element_features(obj1)
                resourceSave = XMIResource(URI(Path + 'temp.xmi'))
                resourceSave.use_uuid = True
                resourceSave.append(obj1)
                resourceSave.save()
                resourceSave.save(output=URI(Path + 'temp.xmi'))
                with open(Path + 'temp.xmi', 'r') as file:
                        myFile = file.read()
                file.close()
                addedElements.append( {'operation': 'DEL', 'internal_id': obj1.eGet('_internal_id'), 'container_id': container_id, 'file_source_xmi': myFile, 'element_References': delfetu[1]} )

        VersionR = self.importModel(VersionRightPath, MyMetaModel)

        for obj1 in VersionR.eAllContents():
            bloomKey00 = obj1.eGet('_internal_id')         
            if ((bloomKey00 in Bloom_base) == False):

                container_id = obj1.eContainer().eGet('_internal_id')
                delfetu = self.get_deleted_element_features(obj1)
                resourceSave = XMIResource(URI(Path + 'temp.xmi'))
                resourceSave.use_uuid = True
                resourceSave.append(obj1)
                resourceSave.save()
                resourceSave.save(output=URI(Path + 'temp.xmi'))
                with open(Path + 'temp.xmi', 'r') as file:
                        myFile = file.read()
                file.close()
                addedElements.append( {'operation': 'DEL', 'internal_id': obj1.eGet('_internal_id'), 'container_id': container_id, 'file_source_xmi': myFile, 'element_References': delfetu[1]} )

        return addedElements 
    
    def get_deleted_element_features(self, deletedElement):
        deleted_elements_Info = ""
        delElement_INFO = []

        for y in deletedElement._isset:
                if ( (y.eClass.name == "EReference")): #and (y.name != "features")
                        
                        if (type(deletedElement.eGet(y.name)).__name__ == "EOrderedSet") or (type(deletedElement.eGet(y.name)).__name__ == "ESet"):
                                deleted_elements_Info = deleted_elements_Info + y.name + "->"
                                tempp =[]

                                for ob in deletedElement.eGet(y.name):
                                        deleted_elements_Info = deleted_elements_Info + ob.eGet('_internal_id') + "-"
                                        tempp.append(ob.eGet('_internal_id'))
                                deleted_elements_Info = deleted_elements_Info + ","

                                if tempp:
                                    delITEM = {'feature_name': y.name, 'feature_value': tempp}
                                    delElement_INFO.append(delITEM)
                        
                        else:
                                
                                deleted_elements_Info = deleted_elements_Info + y.name + "->"
                                deleted_elements_Info = deleted_elements_Info + deletedElement.eGet(y.name).eGet('_internal_id') + ","

                                delITEM = {'feature_name': y.name, 'feature_value': deletedElement.eGet(y.name).eGet('_internal_id')}
                                delElement_INFO.append(delITEM)

        return deleted_elements_Info , delElement_INFO
    
    def get_Part_of_my_file(self, contentVersionInfo, End, Start):
        flagFile = False
        partOf_myFile =""
        for ii in contentVersionInfo:
            if (str(ii.replace("\n",'')) == End):
              flagFile = False
            if (flagFile == True):
              partOf_myFile = partOf_myFile + ii
            if (str(ii.replace("\n",'')) == Start):
              flagFile = True
        return partOf_myFile
    
    def remove_elements_OF_current_model(self, currentModel, add_Json):
        for add_item in add_Json:
            for i in currentModel.eAllContents():
                try:
                    if (i.eGet('_internal_id') == add_item['internal_id'] ):
                        i.delete()
                except AttributeError:
                    print("AttributeError: Feature is read-only")
                # Feature is read-only, skip
                    continue
             
    # def remove_elements_OF_current_model(self, currentModel, add_Json):
    #     # Collect elements to delete first to avoid modifying the iterator while looping
    #     elements_to_delete = []

    #     for add_item in add_Json:
    #         for i in currentModel.eAllContents():
    #             try:
    #                 if i.eGet('_internal_id') == add_item['internal_id']:
    #                     elements_to_delete.append(i)
    #             except AttributeError:
    #                 # Some objects might not have _internal_id
    #                 continue

    #     for eobj in elements_to_delete:
    #         # Only delete if it's safe (not part of a read-only or derived feature)
    #         try:
    #             # Check if eobj is contained in a read-only or derived feature
    #             container = eobj.eContainer()
    #             if container is None:
    #                 # Top-level object, safe to delete
    #                 eobj.delete()
    #             else:
    #                 feature = eobj.eContainingFeature
    #                 if feature.derived or feature.transient:
    #                     # Skip read-only/derived features
    #                     continue
    #                 else:
    #                     eobj.delete()
    #         except AttributeError:
    #             # Feature is read-only, skip
    #             continue

    # def remove_elements_OF_current_model(self, currentModel, add_Json):
    #     # Collect elements to delete first
    #     elements_to_delete = []

    #     # Find elements matching the internal_id
    #     for add_item in add_Json:
    #         for i in currentModel.eAllContents():
    #             try:
    #                 if i.eGet('_internal_id') == add_item['internal_id']:
    #                     elements_to_delete.append(i)
    #             except AttributeError:
    #                 continue


    #     # --- Helper: safe containment feature lookup ---
    #     def find_containing_feature(eobj):
    #         container = eobj.eContainer()
    #         if container is None:
    #             return None

    #         # Search for the containment reference in the container
    #         for ref in container.eClass.eAllReferences():
    #             if not ref.containment:
    #                 continue

    #             value = getattr(container, ref.name)

    #             if ref.many:
    #                 if eobj in value:
    #                     return ref
    #             else:
    #                 if value is eobj:
    #                     return ref

    #         return None


    #     # --- Safe deletion loop ---
    #     for eobj in elements_to_delete:
    #         container = eobj.eContainer()

    #         # 1. No container → root element → safe to delete
    #         if container is None:
    #             eobj.delete()
    #             continue

    #         # 2. Find containing feature WITHOUT triggering AttributeError
    #         feature = find_containing_feature(eobj)
    #         if feature is None:
    #             # Cannot determine containment → safest to skip
    #             continue

    #         # 3. Skip read-only features
    #         if not feature.changeable:
    #             continue

    #         # 4. Skip non-containment features (should not happen after find_containing_feature)
    #         if not feature.containment:
    #             continue

    #         # 5. Skip derived features (computed values)
    #         if feature.derived:
    #             continue

    #         # 6. Safe to delete
    #         eobj.delete()


        
        # AddedElements_List = AddedElements.split("element")
    
        # for one_elem in AddedElements_List:
            
        #     if(one_elem == ''):
        #           ddd=5
        #     else:
                
        #         one_elem = one_elem.replace("\n","",1)
                
        #         with open(Mypath + "temp.xmi", 'w') as file:
        #             file.write(one_elem)
        #         file.close()

        #         metaModel = self.importMetaModel(PathmetaModel)
        #         MyModel_Added_Elements = self.importModel(Mypath+'temp.xmi', metaModel)
                
        #         for i in currentModel.eAllContents():
        #             #for j in MyModel_Added_Elements.eAllContents():
                        
        #                 if (i.eGet('_internal_id') == MyModel_Added_Elements.eGet('_internal_id')):       ###### based on UUID of elements
        #                         i.delete()

    def add_elements_TO_current_model(self, currentModel, metaModel, Mypath, delete_Json):
        
        # rset = ResourceSet()
        # resource = rset.get_resource(URI(Mypath + 'Families.ecore'))
        # mm_root = resource.contents[0]
        # rset.metamodel_registry[mm_root.nsURI] = mm_root
        # At this point, the .ecore is loaded in the 'rset' as a metamodel

        for delete_item in delete_Json:

            with open(Mypath + "temp.xmi", 'w') as file:
                file.write(delete_item['file_source_xmi'])
            file.close()
            
            #resource = rset.get_resource(URI(Mypath + 'temp.xmi'))
            #print(resource.contents[0])
            #model_root = resource.contents[0]
            # At this point, the model instance is loaded!

            #MyModel_Added_Elements = model_root
            MyModel_Added_Elements = self.importModel(Mypath+'temp.xmi', metaModel)
            list_delete_item = delete_item['element_References']
            for elm in list_delete_item:
                self.set_att_new_element(currentModel, MyModel_Added_Elements, elm)            
            

        # AddedElements_List = DeletedElements.split("element")
        # DeletedElements_Detail = DeletedElements_Detail.split("\n")
        
        # for one_elem in AddedElements_List:
            
        #     if(one_elem == ''):
        #           ddd=5
        #     else:
                
        #         one_elemm = one_elem.replace("\n","",1)

        #         open(Mypath + 'temp.xmi', 'w').close()

        #         with open(Mypath + "temp.xmi", 'w') as file:
        #             file.write(one_elemm)
        #         file.close()

                
        #         #MyMetaModel = self.importMetaModel(PathmetaModel)
                
        #         MyModel_Added_Elements = self.importModel(Mypath+'temp.xmi', metaModel)
               
        #         #for i in DeletedElements.eAllContents():
        #         for elm in DeletedElements_Detail:
                    
        #             myString_detail = elm.split('::')
                    
        #             if(MyModel_Added_Elements.eGet('_internal_id') == myString_detail[0]):
        #                 print("111111111")
        #                 print(myString_detail)
        #                 self.set_att_new_element(currentModel, MyModel_Added_Elements, myString_detail[1])
        #             else:
        #                 xo=2
        #                 print("222222")
                       
    def add_elements_TO_model_EVO(self, currentModel, metaModel, MergedModel, Mypath, itemEL, UPDATEITEMS):
            
            self.myHashTable_Object = HashTable(10000)
            self.myList_deletedElement =[]
            flag_dublicate_UUID = False
            
            listElInCmodel = []
            listElInCmodel.append(currentModel.eGet('_internal_id'))
            currentobj = None

            for cobj in currentModel.eAllContents():
                self.myHashTable_Object.insert(cobj.eGet('_internal_id'), cobj)
                listElInCmodel.append(cobj.eGet('_internal_id'))
                if cobj.eGet('_internal_id') == itemEL['internal_id']:
                     currentobj = cobj
                
            # if the element is not added to the model
            if itemEL['internal_id'] not in listElInCmodel:
                with open(Mypath + "temp.xmi", 'w') as file:
                    file.write(itemEL['file_source_xmi'])
                file.close()
                MyModel_Added_Elements = self.importModel(Mypath+'temp.xmi', metaModel)
                
                #Here we check that two element with the same id do not appear in the model, since it makes error!
                for myEl in MyModel_Added_Elements.eAllContents():
                    self.myList_deletedElement.append(myEl.eGet('_internal_id'))
                for item in self.myList_deletedElement:
                    if item in self.myHashTable_Object:
                        for obj0Temp in MyModel_Added_Elements.eAllContents():
                            try:
                                if (obj0Temp.eGet('_internal_id') == item):
                                        obj0Temp.delete()
                                        flag_dublicate_UUID = True
                            except AttributeError:
                                print("AttributeError")
                                continue 
                if flag_dublicate_UUID == True:
                    self.myHashTable_Object = HashTable(10000)
                    for cobj in currentModel.eAllContents():
                        self.myHashTable_Object.insert(cobj.eGet('_internal_id'), cobj)
                        listElInCmodel.append(cobj.eGet('_internal_id'))
                        if cobj.eGet('_internal_id') == itemEL['internal_id']:
                            currentobj = cobj
                ########
    
                list_delete_item = itemEL['element_References']
                for elm in list_delete_item:
                    self.set_att_new_element(currentModel, MyModel_Added_Elements, elm)

                ##
                # This is for an update after adding deleted elements.
                # We do this because deleted element may have no ref inside it, but its container should refer to it.
                # As a result, created model contains deleted element!
                ##
                self.myHashTable_Object.insert(MyModel_Added_Elements.eGet('_internal_id'), MyModel_Added_Elements)
                if UPDATEITEMS:
                    for upItem in UPDATEITEMS:
                         if upItem['internal_id'] == itemEL['container_id']:
                              for upFeature in upItem['feature_value']:
                                   if upFeature == itemEL['internal_id'] and itemEL['operation'] == "DEL":
                                        
                                        if self.myHashTable_Object.search(upItem['internal_id']):
                    
                                            objHT = self.myHashTable_Object.search(upItem['internal_id'])
                                            if "EReference" == upItem['type'] or "EContainer" == upItem['type']:
                                                        if isinstance(upItem['feature_value'], list):
                                                            li_O=[]
                                                            li_id=[]
                                                            for fv in objHT.eGet(upItem['feature_name']):
                                                                li_O.append(fv)
                                                                li_id.append(fv.eGet('_internal_id'))
                                                            for fItem in upItem['feature_value']:
                                                                if fItem not in li_id:
                                                                    if self.myHashTable_Object.search(fItem):
                                                                        li_O.append(self.myHashTable_Object.search(fItem))
                                                            objHT.eSet(upItem['feature_name'], li_O)  
                                                        else:
                                                            #objHT = self.myHashTable_Object.search(upItem['internal_id'])
                                                            if self.myHashTable_Object.search(upItem['feature_value']):
                                                                objRef = self.myHashTable_Object.search(upItem['feature_value'])
                                                                objHT.eSet(upItem['feature_name'], objRef)
                                                            else:
                                                                print('conflict in reverse_updating_elements_model')
                                            else:
                                                #objHT = self.myHashTable_Object.search(upItem['internal_id'])
                                                objHT.eSet(upItem['feature_name'], upItem['feature_value'])

                                            #UPDATEITEMS.remove(upItem)



                                        
                         
                    #self.reverse_updating_elements_model(MyModel, UPDATEITEMS)

            else:
                if currentobj != None:
                    list_delete_item = itemEL['element_References']
                    for elm in list_delete_item:
                        self.set_att_new_element(currentModel, currentobj, elm)

            resourceSave = XMIResource(URI(Mypath + MergedModel))
            resourceSave.use_uuid = True
            resourceSave.append(currentModel)  # We add the root to the resource
            resourceSave.save()  # will save the result in 'my/path.xmi'
            resourceSave.save(output=URI(Mypath + MergedModel))  # save the result in 'test/path.xmi'
            
            

                    
    def set_att_new_element(self, TargetModel, deletedElement, detailElem):
        list_ob_to_set = []

        # obj_Models =[]

        # print("====")
        # print("===s=")
        # for ob in TargetModel.eAllContents():
        #     print(ob.eGet('name'))
        #     print(ob.eContainer())
        #     obj_Models.append(ob)
        # obj_Models.append(TargetModel)
        # print("==s==")
        # print("====")
        for obj0 in TargetModel.eAllContents():
           
            #check if it is list or not
            if isinstance(detailElem['feature_value'], list):
    
                for fv in detailElem['feature_value']:
                    
                    if (obj0.eGet('_internal_id') == fv):

                        list_ob_to_set.append(obj0)
                        #Remove Duplicates From a Python List
                        #list(dict.fromkeys(list_ob_to_set))

                        #deletedElement.eSet(detailElem['feature_name'], list_ob_to_set) 
                    elif(obj0.eGet('_container').eGet('_internal_id') == fv):

                        list_ob_to_set.append(obj0.eGet('_container'))
                        #Remove Duplicates From a Python List
                        #list(dict.fromkeys(list_ob_to_set))

                        #deletedElement.eSet(detailElem['feature_name'], list_ob_to_set)
                
                #Remove Duplicates From a Python List
                if list_ob_to_set:
                    list(dict.fromkeys(list_ob_to_set))
                    if len(list_ob_to_set) == len(detailElem['feature_value']):
                        deletedElement.eSet(detailElem['feature_name'], list_ob_to_set)
                           
            else:
                #check Duplicates because of obj0.eGet('_container'). ! we can have two or more elements with the same _container !
                if deletedElement.eGet(detailElem['feature_name']) is None:

                    if (obj0.eGet('_internal_id') == detailElem['feature_value']):
                        deletedElement.eSet(detailElem['feature_name'], obj0)

                    elif(obj0.eGet('_container')):

                        if(obj0.eGet('_container').eGet('_internal_id') == detailElem['feature_value']):
                            deletedElement.eSet(detailElem['feature_name'], obj0.eGet('_container'))
                            break
        



        # deEl = detailElem.split('->')
        
        # print(deEl[0])
        # print(deEl[1])

        # featuresDel = deEl[1].split(',')
        # print(featuresDel)

        # count = 0
        # ii = 1
        
        # while ( ii <= len(deEl)/2 ):
        #      print("111111")
        #      featuresDel = deEl[count + 1].split(',')
        #      print("222222")
             
        #      print("33333")
        #      jj = 1
        #      while(jj < len(featuresDel)):
        #         print("4444")
        #         for obj0 in TargetModel.eAllContents():
        #              print("555555555")
        #              if (obj0.eGet('_internal_id') == featuresDel[jj-1]):
        #                 print("666666")
        #                 print(deEl[count])
        #                 deletedElement.eSet(deEl[count], obj0)
        #                 print("777777")
        #                 break
        #         jj = jj +1
        #      count = count + 2
        #      ii = ii + 1

        



        
        # for y in deletedElement._isset:
        #         print(y.name)
        #         if ( (y.eClass.name == "EReference")): #and (y.name != "features")
        #                 print(y.name+"99999")
        #                 if (type(deletedElement.eGet(y.name)).__name__ == "EOrderedSet"):
        #                         #counter = len(deletedElement.eGet(y.eGet('UUID_Versioning_System')).items)
        #                         for ob in deletedElement.eGet(y.name):
        #                                 newval = ob.eGet('_internal_id')
        #                                 for obj0 in TargetModel.eAllContents():
        #                                         temp = ob.eClass.name
        #                                         if(obj0.eClass.name == temp):
        #                                                 if (obj0.eGet('_internal_id') == newval):
        #                                                         deletedElement.eGet(y.name)[deletedElement.eGet(y.name).index(ob)] = obj0
        #                                                         break
        #                 else:
        #                         newval = deletedElement.eGet(y.name).eGet('_internal_id')
        #                         print(newval + "++++")
        #                         for obj0 in TargetModel.eAllContents():
        #                                 temp = deletedElement.eGet(y.name).eClass.name
        #                                 if(obj0.eClass.name == temp):
        #                                         if (obj0.eGet('_internal_id') == newval):
        #                                                 deletedElement.eSet(y.name , obj0)
        #                                                 break
    
    def create_UUID_For_All_Elements(self, modelPath):

        MyMetaModelpath = self.MY_METAMODEL_FILE_PATH  #"C:/Users/Admin/Desktop/VSM/simpleOO.ecore"
        #print(MyMetaModelpath)
        MyMetaModel = ResourceSet()
        resource = MyMetaModel.get_resource(URI(MyMetaModelpath))
        mm_root = resource.contents[0]
        MyMetaModel.metamodel_registry[mm_root.nsURI] = mm_root
        
        myModel = self.importModel(modelPath, MyMetaModel)

         # Seting UUID for Elements in the model using uuid.uuid4().hex
        # for obj in myModel.eAllContents():
        #      if (obj._internal_id == None):
        #          obj.eSet('_internal_id' , str(uuid.uuid4().hex))
        
        # SAVE MY MODEL
        resourceSave = XMIResource(URI(modelPath))
        resourceSave.use_uuid = True
        resourceSave.append(myModel) 
        resourceSave.save()  
        resourceSave.save(output=URI(modelPath))  

    def reverse_updating_elements_model(self, currentModel, update_Json):

        self.myHashTable_Object = HashTable(10000)       #%%%%%%%%%%%%%%%%%%%% size table
        for obj0 in currentModel.eAllContents():
             self.myHashTable_Object.insert(obj0.eGet('_internal_id'), obj0)
        
        temp =[]
        for upItem in update_Json:
            add_list_item = []

            if "ADD" == upItem['operation']:
                #temp.append(upItem.copy())
                #update_Json.remove(upItem)
                if self.myHashTable_Object.search(upItem['internal_id']): #(upItem['internal_id'] in self.myHashTable_Object):
                    objHT = self.myHashTable_Object.search(upItem['internal_id'])
                    if "EReference" == upItem['type'] or "EContainer" == upItem['type']:
                        #if (upItem['internal_id'] in self.myHashTable_Object):
                            #objHT = self.myHashTable_Object.search(upItem['internal_id'])
                            if isinstance(upItem['feature_value'], list):
                                for fv in objHT.eGet(upItem['feature_name']):
                                    if fv.eGet('_internal_id') not in upItem['feature_value']:
                                        add_list_item.append(fv)
                                        
                                if add_list_item:
                                    objHT.eSet(upItem['feature_name'], add_list_item)   

                            #check this line         
                            else:
                                objHT.eSet(upItem['feature_name'], None)
                    else:
                        #objHT = self.myHashTable_Object.search(upItem['internal_id'])
                        objHT.eSet(upItem['feature_name'], None)
        
        for upItem in update_Json:
            if "DEL" == upItem['operation']:
                #update_Json.remove(upItem)
                if self.myHashTable_Object.search(upItem['internal_id']): #self.myHashTable_Object.__contains__(upItem['internal_id']):#(upItem['internal_id'] in self.myHashTable_Object):
                    
                    objHT = self.myHashTable_Object.search(upItem['internal_id'])
                    if "EReference" == upItem['type'] or "EContainer" == upItem['type']:
                                if isinstance(upItem['feature_value'], list):
                                    li_O=[]
                                    li_id=[]
                                    for fv in objHT.eGet(upItem['feature_name']):
                                        li_O.append(fv)
                                        li_id.append(fv.eGet('_internal_id'))
                                    for fItem in upItem['feature_value']:
                                        if fItem not in li_id:
                                            if self.myHashTable_Object.search(fItem):
                                                li_O.append(self.myHashTable_Object.search(fItem))
                                    if sorted(upItem['feature_value']) != sorted(li_id):
                                        objHT.eSet(upItem['feature_name'], li_O)  
                                else:
                                    #objHT = self.myHashTable_Object.search(upItem['internal_id'])
                                    if self.myHashTable_Object.search(upItem['feature_value']):
                                        objRef = self.myHashTable_Object.search(upItem['feature_value'])
                                        if (objHT.eGet(upItem['feature_name']) == None):
                                            objHT.eSet(upItem['feature_name'], objRef)
                                    else:
                                        print('conflict in reverse_updating_elements_model')
                    else:
                      #objHT = self.myHashTable_Object.search(upItem['internal_id'])
                      objHT.eSet(upItem['feature_name'], upItem['feature_value'])

    ########################
    ####comparing models using UUID
    ##
    #
    def Three_Way_Merging_Compare_UUID(self, filepath, metamodelPath, LeftVersion, RightVersion, BaseVersion, MergedModel, Conflict_Decision, Conflict_Decision_Keep_list):

        MyMetaModel = self.importMetaModel(metamodelPath)
        #LeftModel = self.importModel(filepath + LeftVersion, MyMetaModel)
        #RightModel = self.importModel(filepath + RightVersion, MyMetaModel)
        BaseModel = self.importModel(filepath + BaseVersion, MyMetaModel)
        
        #comparing left version with base version
        ## swithcing base and left due to our backward versioning
        
        self.compare_two_models_UUID(metamodelPath, filepath + LeftVersion, filepath + BaseVersion, filepath)
    
        with open(filepath + 'Version_Info.json', 'r') as jfile:
            dataJson = json.load(jfile)
        jfile.close()

        update_Json_LB = []
        delete_Json_LB = []
        add_Json_LB = []
        
        for dataJson_item in dataJson:
            if 'UPDATE' in dataJson_item:
                update_Json_LB = dataJson_item['UPDATE']
            if 'DELETE' in dataJson_item:
                delete_Json_LB = dataJson_item['DELETE']
            if 'ADD' in dataJson_item:
                add_Json_LB = dataJson_item['ADD']
        
    
        #comparing right version with base version
        ## swithcing base and right due to our backward versioning
        
        self.compare_two_models_UUID(metamodelPath, filepath + RightVersion, filepath + BaseVersion, filepath)
        dataJson = ""
        with open(filepath + 'Version_Info.json', 'r') as jfile:
            dataJson = json.load(jfile)
        jfile.close()

        update_Json_RB = []
        delete_Json_RB = []
        add_Json_RB = []
    
        for dataJson_item in dataJson:
            if 'UPDATE' in dataJson_item:
                update_Json_RB = dataJson_item['UPDATE']
            if 'DELETE' in dataJson_item:
                delete_Json_RB = dataJson_item['DELETE']
            if 'ADD' in dataJson_item:
                add_Json_RB = dataJson_item['ADD']


        ##  ###### considering ----right---- version
       
       

        #if update_Json_RB:
        update_Json_LB = update_Json_LB + update_Json_RB
    
        #if delete_Json_RB:
        delete_Json_LB = delete_Json_LB + delete_Json_RB
    
        #if add_Json_RB:
        add_Json_LB = add_Json_LB + add_Json_RB
            


        # Check for conflict decision and remove from the list
        if Conflict_Decision is not None:
            for conflict_item in Conflict_Decision:
                if conflict_item in update_Json_LB:
                    update_Json_LB.remove(conflict_item)
                if conflict_item in delete_Json_LB:
                    delete_Json_LB.remove(conflict_item)
                if conflict_item in add_Json_LB:
                    add_Json_LB.remove(conflict_item)

        # Check for conflicting element should apply at end of the process
        # So, we place them at the end of the list
        if Conflict_Decision_Keep_list is not None:
            for item_keep in Conflict_Decision_Keep_list:
                if item_keep in update_Json_LB:
                    update_Json_LB.append(update_Json_LB.pop(update_Json_LB.index(item_keep)))
                if item_keep in delete_Json_LB:
                    delete_Json_LB.append(delete_Json_LB.pop(delete_Json_LB.index(item_keep)))
                if item_keep in add_Json_LB:
                    add_Json_LB.append(add_Json_LB.pop(add_Json_LB.index(item_keep)))

        
        ####
        ###
        ##
        #Creating merged version

        ###### considering ----left----Right---- version
        ##### modifying base version to create merged version

        

        count_Base = 0
        for item in delete_Json_LB:
            if count_Base == 0:
                #MyMetaModel = self.importMetaModel(self.MY_METAMODEL_FILE_PATH)
                #BaseModel = self.importModel(Mypath + BaseVersion, MyMetaModel)
                self.add_elements_TO_model_EVO(BaseModel, MyMetaModel, MergedModel, filepath, item, update_Json_LB)
                count_Base = 1
            else:
                MyMetaModel = self.importMetaModel(self.MY_METAMODEL_FILE_PATH)
                BaseModeltemp = self.importModel(filepath + MergedModel, MyMetaModel)
                BaseModel = BaseModeltemp
                self.add_elements_TO_model_EVO(BaseModeltemp, MyMetaModel, MergedModel, filepath, item, update_Json_LB)
             
        #print("Add")
        if update_Json_LB:
            self.reverse_updating_elements_model(BaseModel, update_Json_LB)

        if add_Json_LB:
            self.remove_elements_OF_current_model(BaseModel, add_Json_LB)

        ###### considering ----right---- version
        ##### modifying base version to create merged version
        
        # if add_Json_RB:
        #      self.remove_elements_OF_current_model(BaseModel, add_Json_RB)
        
        # count_Base = 0
        # for item in delete_Json_RB:
        #     if count_Base == 0:
        #         #MyMetaModel = self.importMetaModel(self.MY_METAMODEL_FILE_PATH)
        #         #BaseModel = self.importModel(Mypath + BaseVersion, MyMetaModel)
        #         self.add_elements_TO_model_EVO(BaseModel, MyMetaModel, BaseVersion, filepath, item)
        #         count_Base = 1
        #     else:
        #         MyMetaModel = self.importMetaModel(self.MY_METAMODEL_FILE_PATH)
        #         BaseModel = self.importModel(filepath + BaseVersion, MyMetaModel)
        #         #BaseModel = BaseModel
        #         self.add_elements_TO_model_EVO(BaseModel, MyMetaModel, BaseVersion, filepath, item)
             
        # #print("Add")
        # if update_Json_RB:
        #     self.reverse_updating_elements_model(BaseModel, update_Json_RB)







         # SAVE MY MODEL
        resourceSave = XMIResource(URI(filepath + MergedModel))
        resourceSave.use_uuid = True
        resourceSave.append(BaseModel)  # We add the root to the resource
        resourceSave.save()  # will save the result in 'my/path.xmi'
        resourceSave.save(output=URI(filepath + MergedModel))  # save the result in 'test/path.xmi'
        print("....Merged Model is CREATED....")

         

    #comparing models using bloom filter ####
    ########
    ###
    ##
    #
    def Three_Way_Merging(self, filepath, metamodelPath, LeftVersion, RightVersion, BaseVersion, MergedModel):
         
        # MyMetaModel = self.importMetaModel(metamodelPath)
        # LeftModel = self.importModel(filepath + LeftVersion, MyMetaModel)
        # RightModel = self.importModel(filepath + RightVersion, MyMetaModel)
        # BaseModel = self.importModel(filepath + BaseVersion, MyMetaModel)

        LeftModel_bloom = self.createBloom_with_path_version(filepath + LeftVersion, metamodelPath )
        RightModel_bloom = self.createBloom_with_path_version(filepath + RightVersion, metamodelPath)
        BaseModel_bloom = self.createBloom_with_path_version(filepath + BaseVersion, metamodelPath)
        
        ##
        #return id of the elements
        # deleted elements from base version
        ##
        deleted_from_Left = self.identify_deleted_elements_BLOOMFILTER(LeftModel_bloom, filepath + BaseVersion, metamodelPath)
        deleted_from_Right = self.identify_deleted_elements_BLOOMFILTER(RightModel_bloom, filepath + BaseVersion, metamodelPath)
        ##
        #return elements
        added_Left_Right = self.identify_added_elements_BLOOMFILTER(BaseModel_bloom,  filepath + LeftVersion, filepath + RightVersion, filepath)
        #added_from_Left = self.identify_added_elements_BLOOMFILTER(BaseModel_bloom,  filepath + LeftVersion, metamodelPath, MyMetaModel, BaseModel)
        #added_from_Right = self.identify_added_elements_BLOOMFILTER(BaseModel_bloom,  filepath + RightVersion, metamodelPath)
        #added_Left_Right.reverse()
        
        count_Base = 0
        for item in added_Left_Right:
            if count_Base == 0:
                MyMetaModel = self.importMetaModel(self.MY_METAMODEL_FILE_PATH)
                BaseModel = self.importModel(filepath + BaseVersion, MyMetaModel)
                self.add_elements_TO_model_EVO(BaseModel, MyMetaModel, MergedModel, filepath, item)
                count_Base = 1
            else:
                MyMetaModel = self.importMetaModel(self.MY_METAMODEL_FILE_PATH)
                BaseModel = self.importModel(filepath + MergedModel, MyMetaModel)
                self.add_elements_TO_model_EVO(BaseModel, MyMetaModel, MergedModel, filepath, item)
       
        for obj0 in BaseModel.eAllContents():
            try:
                if ( (obj0.eGet('_internal_id') in deleted_from_Left)
                    or 
                    (obj0.eGet('_internal_id') in deleted_from_Right) ):
                        obj0.delete()
            except AttributeError:
                print("AttributeError")
                continue 

        # for obj0 in BaseModel.eAllContents():
        #     try:
        #         obj_id = obj0.eGet('_internal_id')
        #     except AttributeError:
        #         continue  # skip objects without _internal_id

        #     if obj_id in deleted_from_Left or obj_id in deleted_from_Right:
        #         # Check if deletion is allowed
        #         container = obj0.eContainer()
        #         if container is None:
        #             # top-level object, safe to delete
        #             obj0.delete()
        #         else:
        #             feature = obj0.eContainingFeature
        #             if feature.derived or feature.transient:
        #                 # skip read-only / derived features
        #                 continue
        #             else:
        #                 obj0.delete()




















        # for obj in BaseModel.eAllContents():
             
        #      for objAdd in added_from_Left:
                
        #         if ( BaseModel.eGet('_internal_id') == objAdd.eContainer().eGet('_internal_id') ):
        #             #objAdd.eSet(objAdd.eContainer() , BaseModel)
        #             objAdd.eSet('_container',BaseModel)
        #             print("7")


        #         if ( obj.eGet('_internal_id') == objAdd.eContainer().eGet('_internal_id') ):
        #             #objAdd.eSet( objAdd.eContainer() , obj)
        #             objAdd.eSet('_container',obj)
        #             print("7")
        
                 # SAVE MY MODEL
        resourceSave = XMIResource(URI(filepath + MergedModel))
        resourceSave.use_uuid = True
        resourceSave.append(BaseModel)  # We add the root to the resource
        resourceSave.save()  # will save the result in 'my/path.xmi'
        resourceSave.save(output=URI(filepath + MergedModel))  # save the result in 'test/path.xmi'
        print("....Merged Model is CREATED....")





    def Conflict_Detection(self, DIFF_Left_Base, DIFF_Right_Base):
        """
        Detects conflicts between left and right diffs (vs. base).
        Returns categorized conflicts as tuples of lists.
        """

        # --------------------------
        # Helper: parse DIFF into add/delete/update sets
        def _parse_diff(diff):
            updates, deletes, adds = [], [], []
            for d in diff:
                if 'UPDATE' in d:
                    updates = d['UPDATE']
                if 'DELETE' in d:
                    adds = d['DELETE']     # backward versioning: delete = add
                if 'ADD' in d:
                    deletes = d['ADD']     # backward versioning: add = delete
            return updates, deletes, adds

        # --------------------------
        # Helper: process delete–update conflict
        def _process_delete_update_conflict(delete_item, update_item,
                                            delete_update, delete_use_old, delete_move):
            pair = [delete_item, update_item]
            if update_item['type'] == "other":
                delete_update.append(pair)
            elif update_item['type'] == "EContainer":
                delete_move.append(pair)
            else:
                delete_use_old.append(pair)

        # --------------------------
        # Helper: process delete–add conflict
        def _process_delete_add(delete_items, add_items, conflict_list):
            """Check Delete-Add conflicts inside a given version model."""
            for d_item in delete_items:
                for a_item in add_items:
                    for ref in a_item.get('element_References', []):
                        if d_item['internal_id'] == ref['feature_value']:
                            conflict_list.append([d_item, a_item])

        # --------------------------
        # Parse diffs
        update_LEFT, delete_LEFT, add_LEFT = _parse_diff(DIFF_Left_Base)
        update_RIGHT, delete_RIGHT, add_RIGHT = _parse_diff(DIFF_Right_Base)

        # --------------------------
        # Conflicts categories
        CONFLICT_DELETE_UPDATE, CONFLICT_DELETE_USE_OLD, CONFLICT_DELETE_MOVE = [], [], []
        CONFLICT_DELETE_ADD, CONFLICT_UPDATE_UPDATE = [], []
        CONFLICT_MOVE_MOVE, CONFLICT_INSERT_INSERT = [], []

        # --------------------------
        # DELETE <=> UPDATE
        for d in delete_RIGHT:
            for u in update_LEFT:
                if d['internal_id'] == u['internal_id'] and u['operation'] == "DEL":
                    _process_delete_update_conflict(d, u,
                                                    CONFLICT_DELETE_UPDATE,
                                                    CONFLICT_DELETE_USE_OLD,
                                                    CONFLICT_DELETE_MOVE)

        for d in delete_LEFT:
            for u in update_RIGHT:
                if d['internal_id'] == u['internal_id'] and u['operation'] == "DEL":
                    _process_delete_update_conflict(d, u,
                                                    CONFLICT_DELETE_UPDATE,
                                                    CONFLICT_DELETE_USE_OLD,
                                                    CONFLICT_DELETE_MOVE)

        # --------------------------
        # DELETE <=> ADD
        _process_delete_add(delete_RIGHT, add_LEFT, CONFLICT_DELETE_ADD)
        _process_delete_add(delete_LEFT, add_RIGHT, CONFLICT_DELETE_ADD)

        # -------------------------- operation': 'ADD'
        # UPDATE <=> UPDATE (also handles Move-Move & Insert-Insert)
        in_in_flag = False
        up_up_conflict_list = []
        temp = []
        for u1 in update_RIGHT:
            for u2 in update_LEFT:
                if (u1['internal_id'] == u2['internal_id'] and
                    u1['feature_name'] == u2['feature_name'] and
                    u1['operation'] == u2['operation']):

                    if u1['operation'] == 'ADD':
                        temp.clear()
                        temp.extend([u1, u2])
                    else:
                        temp.extend([u1, u2])
                        if u1['feature_value'] == u2['feature_value']:
                            continue

                    # Case: type = other → Update-Update
                    if u1['type'] == "other" or u2['type'] == "other":
                        if not (isinstance(u1['feature_value'], list) or isinstance(u2['feature_value'], list)):
                            if (len(temp) == 4):
                                CONFLICT_UPDATE_UPDATE.append(temp.copy())
                                up_up_conflict_list.extend(temp)
                        continue

                    # Case: container-related
                    if u1['type'] == "EContainer" or u2['type'] == "EContainer":
                        if (u1['feature_value'] is None or u2['feature_value'] is None) or in_in_flag:
                            in_in_flag = False  # only once
                            if (len(temp) == 4):
                                CONFLICT_INSERT_INSERT.append(temp.copy())
                                up_up_conflict_list.extend(temp)
                            if u1['feature_value'] is None or u2['feature_value'] is None:
                                in_in_flag = True
                        else:
                            if (len(temp) == 4):
                                CONFLICT_MOVE_MOVE.append(temp.copy())
                                up_up_conflict_list.extend(temp)
                    else:
                        # Default Update-Update
                        if not (isinstance(u1['feature_value'], list) or isinstance(u2['feature_value'], list)):
                            if (len(temp) == 4):
                                CONFLICT_UPDATE_UPDATE.append(temp.copy())
                                up_up_conflict_list.extend(temp)

        # in case that property is none and both users add new value to it.
        for u1 in update_RIGHT:
            for u2 in update_LEFT:
                if (u1['internal_id'] == u2['internal_id'] and
                    u1['feature_name'] == u2['feature_name'] and
                    u1['operation'] == "DEL" and u2['operation'] == "DEL" and 
                    u1 not in up_up_conflict_list and u2 not in up_up_conflict_list):

                    if u1['feature_value'] == u2['feature_value']:
                        continue
                    temp.clear()
                    temp.extend([u1, u2])
                    # Case: type = other → Update-Update
                    if u1['type'] == "other" or u2['type'] == "other":
                        if not (isinstance(u1['feature_value'], list) or isinstance(u2['feature_value'], list)):
                            CONFLICT_UPDATE_UPDATE.append(temp.copy())
                            continue
                    # Case: container-related
                    if u1['type'] == "EContainer" or u2['type'] == "EContainer":
                        if not (isinstance(u1['feature_value'], list) or isinstance(u2['feature_value'], list)):
                            CONFLICT_INSERT_INSERT.append(temp.copy())
                    else:
                        # Default Update-Update
                        if not (isinstance(u1['feature_value'], list) or isinstance(u2['feature_value'], list)):
                            CONFLICT_UPDATE_UPDATE.append(temp.copy())

        self.CONFLICT_DELETE_ADD = CONFLICT_DELETE_ADD
        self.CONFLICT_DELETE_MOVE = CONFLICT_DELETE_MOVE
        self.CONFLICT_DELETE_UPDATE = CONFLICT_DELETE_UPDATE
        self.CONFLICT_DELETE_USE_OLD = CONFLICT_DELETE_USE_OLD
        self.CONFLICT_INSERT_INSERT = CONFLICT_INSERT_INSERT
        self.CONFLICT_MOVE_MOVE = CONFLICT_MOVE_MOVE
        self.CONFLICT_UPDATE_UPDATE = CONFLICT_UPDATE_UPDATE

        return True
    
        # return (CONFLICT_DELETE_UPDATE,
        #         CONFLICT_DELETE_USE_OLD,
        #         CONFLICT_DELETE_MOVE,
        #         CONFLICT_DELETE_ADD,
        #         CONFLICT_UPDATE_UPDATE,
        #         CONFLICT_MOVE_MOVE,
        #         CONFLICT_INSERT_INSERT)
    
    def Prepered_List_of_Conflict_Detection_Resolution_Automatic_Merge(self, DIFF_Left_Base, DIFF_Right_Base):
        # --------------------------
        # Helper: parse DIFF into add/delete/update sets
        def _parse_diff(diff):
            updates, deletes, adds = [], [], []
            for d in diff:
                if 'UPDATE' in d:
                    updates = d['UPDATE']
                if 'DELETE' in d:
                    adds = d['DELETE']     # backward versioning: delete = add
                if 'ADD' in d:
                    deletes = d['ADD']     # backward versioning: add = delete
            return updates, deletes, adds
        #changes on this list will be ignored during merging
        resolution = []
        # --------------------------
        # Parse diffs
        update_LEFT, delete_LEFT, add_LEFT = _parse_diff(DIFF_Left_Base)
        update_RIGHT, delete_RIGHT, add_RIGHT = _parse_diff(DIFF_Right_Base)
        # --------------------------
        # DELETE <=> UPDATE
        for d in delete_RIGHT:
            for u in update_LEFT:
                if d['internal_id'] == u['internal_id']:
                    resolution.append(u.copy())
        for d in delete_LEFT:
            for u in update_RIGHT:
                if d['internal_id'] == u['internal_id']:
                    resolution.append(u.copy())
        # DELETE <=> ADD
        for d_item in delete_LEFT:
                for a_item in add_RIGHT:
                    for ref in a_item.get('element_References', []):
                        if d_item['internal_id'] == ref['feature_value']:
                            resolution.append(a_item.copy())
        for d_item in delete_RIGHT:
                for a_item in add_LEFT:
                    for ref in a_item.get('element_References', []):
                        if d_item['internal_id'] == ref['feature_value']:
                            resolution.append(a_item.copy())  
        # UPDATE <=> UPDATE (also handles Move-Move & Insert-Insert)
        in_in_flag = False
        up_up_conflict_list = []
        temp = []
        for u1 in update_RIGHT:
            for u2 in update_LEFT:
                if (u1['internal_id'] == u2['internal_id'] and
                    u1['feature_name'] == u2['feature_name'] and
                    u1['operation'] == u2['operation']):
                    if u1['operation'] == 'ADD':
                        temp.clear()
                        temp.extend([u2])
                    else:
                        temp.extend([u2])
                    if u1['feature_value'] == u2['feature_value']:
                        continue
                    # Case: type = other → Update-Update
                    if u1['type'] == "other" or u2['type'] == "other":
                        if not (isinstance(u1['feature_value'], list) or isinstance(u2['feature_value'], list)):
                            if (len(temp) == 2):
                                resolution.extend(temp)
                                up_up_conflict_list.extend(temp)
                        continue
                    # Case: container-related
                    if u1['type'] == "EContainer" or u2['type'] == "EContainer":
                        if (u1['feature_value'] is None or u2['feature_value'] is None) or in_in_flag:
                            in_in_flag = False  # only once
                            if (len(temp) == 2):
                                resolution.extend(temp)
                                up_up_conflict_list.extend(temp)
                            if u1['feature_value'] is None or u2['feature_value'] is None:
                                in_in_flag = True
                        else:
                            if (len(temp) == 2):
                                resolution.extend(temp)
                                up_up_conflict_list.extend(temp)
                    else:
                        # Default Update-Update
                        if not (isinstance(u1['feature_value'], list) or isinstance(u2['feature_value'], list)):
                            if (len(temp) == 2):
                                resolution.extend(temp)
                                up_up_conflict_list.extend(temp)
        # in case that property is none and both users add new value to it.
        for u1 in update_RIGHT:
            for u2 in update_LEFT:
                if (u1['internal_id'] == u2['internal_id'] and
                    u1['feature_name'] == u2['feature_name'] and
                    u1['operation'] == "DEL" and u2['operation'] == "DEL" and 
                    u1 not in up_up_conflict_list and u2 not in up_up_conflict_list):
                    if u1['feature_value'] == u2['feature_value']:
                        continue
                    # Case: type = other → Update-Update
                    if u1['type'] == "other" or u2['type'] == "other":
                        if not (isinstance(u1['feature_value'], list) or isinstance(u2['feature_value'], list)):
                            resolution.append(u2.copy())
                            continue
                    # Case: container-related
                    if u1['type'] == "EContainer" or u2['type'] == "EContainer":
                        if not (isinstance(u1['feature_value'], list) or isinstance(u2['feature_value'], list)):
                            resolution.append(u2.copy())
                    else:
                        # Default Update-Update
                        if not (isinstance(u1['feature_value'], list) or isinstance(u2['feature_value'], list)):
                            resolution.append(u2.copy())

        return resolution


    def _set_conflict(self, attr, value):
        setattr(self, attr, value)
        return True

    def _get_conflict(self, attr):
        return getattr(self, attr)

    @property
    def CONFLICT_DELETE_UPDATE(self):
        return self._get_conflict('_CONFLICT_DELETE_UPDATE')

    @CONFLICT_DELETE_UPDATE.setter
    def CONFLICT_DELETE_UPDATE(self, value):
        self._set_conflict('_CONFLICT_DELETE_UPDATE', value)

    @property
    def CONFLICT_DELETE_USE_OLD(self):
        return self._get_conflict('_CONFLICT_DELETE_USE_OLD')

    @CONFLICT_DELETE_USE_OLD.setter
    def CONFLICT_DELETE_USE_OLD(self, value):
        self._set_conflict('_CONFLICT_DELETE_USE_OLD', value)

    @property
    def CONFLICT_DELETE_MOVE(self):
        return self._get_conflict('_CONFLICT_DELETE_MOVE')

    @CONFLICT_DELETE_MOVE.setter
    def CONFLICT_DELETE_MOVE(self, value):
        self._set_conflict('_CONFLICT_DELETE_MOVE', value)

    @property
    def CONFLICT_DELETE_ADD(self):
        return self._get_conflict('_CONFLICT_DELETE_ADD')

    @CONFLICT_DELETE_ADD.setter
    def CONFLICT_DELETE_ADD(self, value):
        self._set_conflict('_CONFLICT_DELETE_ADD', value)

    @property
    def CONFLICT_UPDATE_UPDATE(self):
        return self._get_conflict('_CONFLICT_UPDATE_UPDATE')

    @CONFLICT_UPDATE_UPDATE.setter
    def CONFLICT_UPDATE_UPDATE(self, value):
        self._set_conflict('_CONFLICT_UPDATE_UPDATE', value)

    @property
    def CONFLICT_MOVE_MOVE(self):
        return self._get_conflict('_CONFLICT_MOVE_MOVE')

    @CONFLICT_MOVE_MOVE.setter
    def CONFLICT_MOVE_MOVE(self, value):
        self._set_conflict('_CONFLICT_MOVE_MOVE', value)

    @property
    def CONFLICT_INSERT_INSERT(self):
        return self._get_conflict('_CONFLICT_INSERT_INSERT')

    @CONFLICT_INSERT_INSERT.setter
    def CONFLICT_INSERT_INSERT(self, value):
        self._set_conflict('_CONFLICT_INSERT_INSERT', value)

    #-----
    def load_left_right_versions(self, MyMetaModel_path, MyModel_V1, MyModel_V2, MyModel_V3):
        MyMetaModel = self.importMetaModel(MyMetaModel_path)
        self.Version_Left = self.importModel(MyModel_V1, MyMetaModel)
        self.Version_Right = self.importModel(MyModel_V2, MyMetaModel)
        self.Version_Base = self.importModel(MyModel_V3, MyMetaModel)
        return True
    def set_Version_Left(self, model):
        self.Version_Left = model
        return True
    def set_Version_Right(self, model):
        self.Version_Right = model
        return True
    def set_Version_Merged(self, model):
        self.Version_Merged = model
        return True

    def get_Version_Left(self):
        return self.Version_Left
    def get_Version_Right(self):
        return self.Version_Right
    def get_Version_Merged(self):
        return self.Version_Merged

    def find_element_in_model_by_ID(self, IDNum, model):
        for obj in model.eAllContents():
            if (IDNum == obj.eGet('_internal_id')):
                return obj



    def find_all_properties_of_element(self, element: EObject,
                                    expand_one_level=True,
                                    limit_children=5):
        """
        Collect all direct properties of a PyEcore EObject in a JSON-safe form.
        Optionally expands referenced EObjects by one level (not deeper),
        and limits the number of displayed child elements for large references.

        Args:
            element (EObject): The PyEcore element to inspect.
            expand_one_level (bool): If True, expand references by one level.
            limit_children (int): Max number of child EObjects to display per reference.
        """
        all_properties = []

        for feature in element._isset:
            value = element.eGet(feature)

            # --- Handle EReferences (links to other EObjects) ---
            if isinstance(feature, EReference):
                if feature.many:
                    value_info = []
                    total = len(value)

                    for i, v in enumerate(value):
                        if limit_children and i >= limit_children:
                            value_info.append({
                                "_info": f"Showing {limit_children} of {total} '{feature.name}' (truncated)"
                            })
                            break

                        if isinstance(v, EObject):
                            if expand_one_level:
                                # Expand one level deep
                                value_info.append(self.find_all_properties_of_element(
                                    v, expand_one_level=False, limit_children=limit_children))
                            else:
                                value_info.append(f"<{v.eClass.name}>")
                        else:
                            value_info.append(str(v))
                else:
                    # Single reference
                    if isinstance(value, EObject):
                        if expand_one_level:
                            value_info = self.find_all_properties_of_element(
                                value, expand_one_level=False, limit_children=limit_children)
                        else:
                            value_info = f"<{value.eClass.name}>"
                    else:
                        value_info = str(value)

            # --- Handle simple attributes ---
            else:
                if isinstance(value, (str, int, float, bool)) or value is None:
                    value_info = value
                elif isinstance(value, (list, set, tuple)):
                    value_info = list(value)
                elif isinstance(value, datetime):
                    value_info = value.isoformat()
                else:
                    value_info = str(value)

            property_info = {
                "feature_name": feature.name,
                "eClass": feature.eContainingClass.name,
                "value": value_info
            }
            all_properties.append(property_info)

        # --- Safely retrieve element ID ---
        feature_names = [f.name for f in element.eClass.eAllStructuralFeatures()]
        element_id = element.eGet('_internal_id') if '_internal_id' in feature_names or element.eGet('_internal_id')!=None else None

        element_properties = {
            "element_type": element.eClass.name,
            "element_id": element_id,
            "properties": all_properties
        }

        return element_properties






    def all_properties_of_model(self, element: EObject, visited=None):
        if visited is None:
            visited = set()

        element_id = getattr(element, '_internal_id', None)
        unique_id = element_id if element_id is not None else id(element)

        if unique_id in visited:
            return {
                "element_type": element.eClass.name,
                "element_id": element_id,
                "note": "Already visited (cycle detected)"
            }
        visited.add(unique_id)

        all_properties = []

        for feature in element._isset:  # or element.eClass.eAllStructuralFeatures()
            value = element.eGet(feature)

            if isinstance(feature, EReference):
                if feature.many:
                    value_info = []
                    for v in value:
                        if isinstance(v, EObject):
                            value_info.append(self.all_properties_of_model(v, visited))
                        else:
                            value_info.append(str(v))
                else:
                    if isinstance(value, EObject):
                        value_info = self.all_properties_of_model(value, visited)
                    else:
                        value_info = str(value)
            else:
                if isinstance(value, (str, int, float, bool)) or value is None:
                    value_info = value
                elif isinstance(value, (list, set, tuple)):
                    value_info = [str(v) if not isinstance(v, (str, int, float, bool)) else v for v in value]
                elif isinstance(value, datetime):
                    value_info = value.isoformat()
                else:
                    value_info = str(value)

            property_info = {
                "feature_name": feature.name,
                "eClass": feature.eContainingClass.name,
                "value": value_info
            }
            all_properties.append(property_info)

        return {
            "element_type": element.eClass.name,
            "element_id": element_id,
            "properties": all_properties
        }










    # def find_all_properties_of_element(self, element):
    #     list_of_properties = []
        
    #     print(element.eGet('_internal_id'))
    #     for property in element._isset:
    #         print(property.eClass.name)
    #         print(property.name)
    #         print(element.eGet(property.name))
    #         pro = pro + {
    #                 "eClass": {property.eClass.name},
    #                 {property.name}: {element.eGet(property.name)}
    #                 }
        
    #     elPro = {
    #         "element ID": {element.eGet('_internal_id')},
    #          pro
    #         }

    # این قطعه کد به خوبی کار میکنه و عنصر مدنظر را به همراه تمام ویژگی هایش نشان میدهد در قالب جیسون
    # def find_all_properties_of_element(self, element: EObject, expand_one_level=True):
    #     """
    #     Collect all direct properties of a PyEcore EObject.
    #     Optionally expands referenced EObjects by one level (not deeper).
    #     Returns a JSON-safe dictionary.
    #     """
    #     all_properties = []

    #     for feature in element._isset:
    #         value = element.eGet(feature)

    #         # --- Handle references ---
    #         if isinstance(feature, EReference):
    #             if feature.many:
    #                 value_info = []
    #                 for v in value:
    #                     if isinstance(v, EObject):
    #                         if expand_one_level:
    #                             # Include child element's direct properties (non-recursive)
    #                             value_info.append(self.find_all_properties_of_element(v, expand_one_level=False))
    #                         else:
    #                             value_info.append(f"<{v.eClass.name}>")
    #                     else:
    #                         value_info.append(str(v))
    #             else:
    #                 if isinstance(value, EObject):
    #                     if expand_one_level:
    #                         value_info = self.find_all_properties_of_element(value, expand_one_level=False)
    #                     else:
    #                         value_info = f"<{value.eClass.name}>"
    #                 else:
    #                     value_info = str(value)

    #         # --- Handle non-reference features ---
    #         else:
    #             if isinstance(value, (str, int, float, bool)) or value is None:
    #                 value_info = value
    #             elif isinstance(value, (list, set, tuple)):
    #                 value_info = list(value)
    #             elif isinstance(value, datetime):
    #                 value_info = value.isoformat()
    #             else:
    #                 value_info = str(value)

    #         property_info = {
    #             "feature_name": feature.name,
    #             "eClass": feature.eContainingClass.name,
    #             "value": value_info
    #         }
    #         all_properties.append(property_info)

    #     # --- Retrieve ID if available ---
    #     feature_names = [f.name for f in element.eClass.eAllStructuralFeatures()]
    #     element_id = element.eGet('_internal_id') if '_internal_id' in feature_names else None

    #     element_properties = {
    #         "element_type": element.eClass.name,
    #         "element_id": element_id,
    #         "properties": all_properties
    #     }

    #     return element_properties




















    # def set_CONFLICT_DELETE_UPDATE(self, conflicts):
    #     self.CONFLICT_DELETE_UPDATE = conflicts
    #     return True
    # def set_CONFLICT_DELETE_USE_OLD(self, conflicts):
    #     self.CONFLICT_DELETE_USE_OLD = conflicts
    #     return True
    # def set_CONFLICT_DELETE_MOVE(self, conflicts):
    #     self.CONFLICT_DELETE_MOVE = conflicts
    #     return True
    # def set_CONFLICT_DELETE_ADD(self, conflicts):
    #     self.CONFLICT_DELETE_ADD = conflicts
    #     return True
    # def set_CONFLICT_UPDATE_UPDATE(self, conflicts):
    #     self.CONFLICT_UPDATE_UPDATE = conflicts
    #     return True
    # def set_CONFLICT_MOVE_MOVE(self, conflicts):
    #     self.CONFLICT_MOVE_MOVE = conflicts
    #     return True
    # def set_CONFLICT_INSERT_INSERT(self, conflicts):
    #     self.CONFLICT_INSERT_INSERT = conflicts
    #     return True
    
    # def get_CONFLICT_DELETE_UPDATE(self):
    #     return self.CONFLICT_DELETE_UPDATE
    # def get_CONFLICT_DELETE_USE_OLD(self):
    #     return self.CONFLICT_DELETE_USE_OLD
    # def get_CONFLICT_DELETE_MOVE(self):
    #     return self.CONFLICT_DELETE_MOVE
    # def get_CONFLICT_DELETE_ADD(self):
    #     return self.CONFLICT_DELETE_ADD
    # def get_CONFLICT_UPDATE_UPDATE(self):
    #     return self.CONFLICT_UPDATE_UPDATE
    # def get_CONFLICT_MOVE_MOVE(self):
    #     return self.CONFLICT_MOVE_MOVE
    # def get_CONFLICT_INSERT_INSERT(self):
    #     return self.CONFLICT_INSERT_INSERT
    





    # def Conflict_Detection(self, DIFF_Left_Base, DIFF_Right_Base):

    #     # رویکرد بکوارد ورژنینگ در شناسایی تغییرات... عملیات حذف به معنی اضافه و برعکس
    #     update_LEFT, delete_LEFT, add_LEFT= [], [], []
    #     for DLB in DIFF_Left_Base:
    #         if 'UPDATE' in DLB:
    #             update_LEFT = DLB['UPDATE']
    #         if 'DELETE' in DLB:
    #             add_LEFT = DLB['DELETE']
    #         if 'ADD' in DLB:
    #             delete_LEFT = DLB['ADD']

    #     update_RIGHT, delete_RIGHT, add_RIGHT = [], [], []
    #     for DRB in DIFF_Right_Base:
    #         if 'UPDATE' in DRB:
    #             update_RIGHT = DRB['UPDATE']
    #         if 'DELETE' in DRB:
    #             add_RIGHT = DRB['DELETE']
    #         if 'ADD' in DRB:
    #             delete_RIGHT = DRB['ADD']

    #     # --------------------------
    #     # --------- DELETE <=> UPDATE

    #     CONFLICT_DELETE_UPDATE = []
    #     CONFLICT_DELETE_USE_OLD = []
    #     CONFLICT_DELETE_MOVE = []

    #     def _process_delete_update_conflict(delete_item, update_item):
    #         pair = [delete_item, update_item]

    #         if update_item['type'] == "other":
    #             CONFLICT_DELETE_UPDATE.append(pair)
    #         elif "EContainer" == update_item['type']:
    #             CONFLICT_DELETE_MOVE.append(pair)
    #         else:
    #             CONFLICT_DELETE_USE_OLD.append(pair)

    #     # Check delete_RIGHT vs update_LEFT
    #     for item1 in delete_RIGHT:
    #         for item2 in update_LEFT:
    #             if item1['internal_id'] == item2['internal_id']:
    #                 _process_delete_update_conflict(item1, item2)

    #     # Check delete_LEFT vs update_RIGHT
    #     for item1 in delete_LEFT:
    #         for item2 in update_RIGHT:
    #             if item1['internal_id'] == item2['internal_id']:
    #                 _process_delete_update_conflict(item1, item2)

    #     # --------------------------
    #     # --------- DELETE <=> ADD
    #     # Delete–Use-New Conflict

    #     CONFLICT_DELETE_ADD = []

    #     def _process_delete_add(delete_items, add_items):
    #         """Check Delete-Add conflicts inside a given version model."""
    #         for d_item in delete_items:
    #             for a_item in add_items:
    #                 for ref in a_item['element_References']:
    #                     if d_item['internal_id'] == ref['feature_value']:
    #                         CONFLICT_DELETE_ADD.append([d_item, a_item])

    #     # Run for both sides
    #     if self.Version_Left and self.Version_Right:
    #         _process_delete_add(delete_RIGHT, add_LEFT)
    #         _process_delete_add(delete_LEFT, add_RIGHT)

    #     IN_IN_flag = False
    #     CONFLICT_UPDATE_UPDATE = []
    #     CONFLICT_MOVE_MOVE = []
    #     CONFLICT_INSERT_INSERT = []

    #     for item1 in update_RIGHT:
    #         for item2 in update_LEFT:
    #             if ( item1['internal_id'] == item2['internal_id'] ) and ( item1['feature_name'] == item2['feature_name'] ) and ( item1['operation'] == item2['operation'] ):
    #                 # Update-Update conflict when either type is "other"
    #                 if item1['type'] == "other" or item2['type'] == "other":
    #                     if not (isinstance(item1['feature_value'], list) or isinstance(item2['feature_value'], list)):
    #                         temp = []
    #                         temp.extend([item1, item2])
    #                         CONFLICT_UPDATE_UPDATE.append(temp)
    #                         continue
                    
    #                 # If either is "container"
    #                 if (item1['type'] == "EContainer" or item2['type'] == "EContainer") :
    #                     # Check feature_value for Insert-Insert conflict
    #                     if (item1['feature_value'] is None or item2['feature_value'] is None) or IN_IN_flag:
    #                         IN_IN_flag = False  # only one extra time
    #                         temp = []
    #                         temp.extend([item1, item2])
    #                         CONFLICT_INSERT_INSERT.append(temp)
    #                         if item1['feature_value'] is None or item2['feature_value'] is None:
    #                             IN_IN_flag = True
    #                     else:
    #                         # Move-Move conflict
    #                         temp = []
    #                         temp.extend([item1, item2])
    #                         CONFLICT_MOVE_MOVE.append(temp)
    #                 else:
    #                     # Default Update-Update conflict
    #                     if not (isinstance(item1['feature_value'], list) or isinstance(item2['feature_value'], list)):
    #                         temp = []
    #                         temp.extend([item1, item2])
    #                         CONFLICT_UPDATE_UPDATE.append(temp)

        
    #     return CONFLICT_DELETE_UPDATE, CONFLICT_DELETE_USE_OLD, CONFLICT_DELETE_MOVE, CONFLICT_DELETE_ADD, CONFLICT_UPDATE_UPDATE, CONFLICT_MOVE_MOVE, CONFLICT_INSERT_INSERT
        
