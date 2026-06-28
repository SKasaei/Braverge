from pyecore.resources import ResourceSet, URI
from pyecore.utils import dispatch

from pyecore.resources.xmi import XMIResource

from pyecore.notification import EObserver, Kind
from pyecore.ecore import EClass, EAttribute, EString, EObject, EPackage
import pyecore.ecore as ecore
from pyecore.commands import Set
import uuid # to create uuid
from pyecore.commands import CommandStack
from pyecore.ecore import EcoreUtils



rset = ResourceSet()
resource = rset.get_resource(URI('Family.ecore'))
mm_root = resource.contents[0]
rset.metamodel_registry[mm_root.nsURI] = mm_root
# At this point, the .ecore is loaded in the 'rset' as a metamodel

resource = rset.get_resource(URI('Family.xmi'))
Se_Mod = resource.contents[0]
# # At this point, the model instance is loaded!

#resourced = rset.get_resource(URI('uni2.xmi'))
#Se_Modeld = resourced.contents[0]


# rset8 = ResourceSet()
# resource8 = rset8.get_resource(URI('simpleOO.ecore'))
# mm_root8 = resource8.contents[0]
# rset8.metamodel_registry[mm_root8.nsURI] = mm_root8

# resourced8 = rset8.get_resource(URI('uni.xmi'))
# Se_Mod = resourced8.contents[0]


#for obj in Se_Modeld.eAllContents():
        # if (obj._internal_id == None):

        #         obj.eSet('_internal_id' , str(uuid.uuid4().hex))
        # for oo in Se_Mod.eAllContents():
        #         if(obj._container.name == oo._container.name):
        #                 print(obj.name)
#        print(obj._internal_id)


# # Seting UUID for Elements in the model using uuid.uuid4().hex
# for obj in Se_Modeld.eAllContents():

#         print(obj.name)
        
#         if ( ('UUID_Versioning_System' not in dir(obj) ) ):
                        
#                         # if ( ( obj.eClass.name == "Class")):
#                         #         p = obj.package
#                         #         print(obj.package.name + "***")
                
#                         obj.eClass.eStructuralFeatures.append(EAttribute('UUID_Versioning_System', EString))
#                         #print(obj.package.name + "***")
#                         # if ( ( obj.eClass.name == "Class")):
#                         #          print(obj.package.name + "***")
#                         #          obj.eSet('package', p)
#                         #          print(obj.package.name + "***")

                        
#         if(obj.eGet('UUID_Versioning_System') == None):
#                 obj.eSet('UUID_Versioning_System', str(uuid.uuid4().hex))
                


# rr = "f121c918539f4234b6e5f32d00100c94::"
# myString_detail = rr.split('::')
# if(myString_detail[1] == ""):

#         print(myString_detail[0])

# x = ""
# cc = ""
# for obj in Se_Mod.eAllContents():
#           print(obj._internal_id)
#           print(obj.name)
#           if obj.name == "student":
#                   x  = obj
#           if obj.name == "tName":
#                   print(obj.eContainer())
#                   #obj.eContainer().delete()
#                   #obj.eContainer().Add(x)
#                   #obj.eSet("eContainer" , x) 
#                   print(obj.eContainer().eGet('_internal_id'))
#                   print("===")
#                   containing_feature = obj.eContainmentFeature()
#                   cc = containing_feature
#                   print(containing_feature)
#                   if containing_feature.many:
#                         x.eGet(containing_feature).append(obj)
#                         print("jjj")
#                   else:
#                         x.eSet(containing_feature, obj)  # if this is a single value
#                         print("hhh")
#                   print("===")
         

#print(dir(Se_Mod))
# print(Second_Model.name)
# print(dir(Second_Model))
# print(Second_Model._isset)
# bb = x._isset
# print(x._isset)
# for u in x._isset:
#      if u.name == "package":
#         print(u.name)
#         for i in Se_Modeld.eAllContents():
#                 if ( (i.name == "mm")): 
#                         # print(i.name)
#                         # x.eSet(x.eGet(u.name), i)
#                         # print(x.package)
#                         x.eSet('_container', i)
#                         print(x._container.name)
#                         print(dir(x))
#                         x.eSet('package', i)

# print(Second_Model.extendedBy[0])
# print(Second_Model.extendedBy[1].name)
# print(Second_Model.extends.name)
# print(Second_Model.name)





# f = open("info.txt", "r")
# oo = f.readlines()

# for e in oo:
#     print(str(e.replace("\n",'')))

# #x = f.readline()
# f = open("info.txt", "r")
# x = f.readline()
# print(x.replace("\n",''))
# if (str(x.replace("\n",'')) == "Element"):
#     print("sajad")




# f = open("info.txt", "r")
# read_myFile = f.readlines()

# print(read_myFile)

# flag = False
# partOf_myFile =""
# for i in read_myFile:
#     if (str(i.replace("\n",'')) == "End_features"):
#       flag = False
#     if (flag == True):
#       partOf_myFile = partOf_myFile + i
#     if (str(i.replace("\n",'')) == "Start_features"):
#       flag = True

# print(partOf_myFile)

# f = open("add.txt", "w")
# f.write(partOf_myFile)





# for obj in Second_Model.eAllContents():
#          print(obj.name)


# resourceSave = XMIResource(URI('a.xmi'))
# for obj0 in Second_Model.eAllContents():
#         if ( obj0.eGet('UUID_Versioning_System')== "e599cdeb03604def8eefe937611eef15"):
#        # if(obj0.eClass.name == "Class"):
#                 # print(obj0.name)
#                 # if ((obj0.name == "teacher") or (obj0.name == "student") or (obj.name == "Education") ):
                        
#                         print(obj0.name)
                        
#                         resourceSave.append(obj0)

# resourceSave.save()
# resourceSave.save(output=URI('a.xmi'))


# resourced = rset.get_resource(URI('a.xmi'))
# Se_Modeld = resourced.contents[0]

# for obj in Se_Modeld.eAllContents():
#         print(obj.name)



# # SAVE MY MODEL
# resourceSave = XMIResource(URI('bb.ecore'))
# resourceSave.append(mm_root)  # We add the root to the resource
# resourceSave.save()  # will save the result in 'my/path.xmi'
# resourceSave.save(output=URI('bb.ecore'))  # save the result in 'test/path.xmi'

rset = ResourceSet()
resource = rset.get_resource(URI('Family.ecore'))
mm_root = resource.contents[0]
rset.metamodel_registry[mm_root.nsURI] = mm_root
# At this point, the .ecore is loaded in the 'rset' as a metamodel

resource = rset.get_resource(URI('Family.xmi'))
Se_Mod = resource.contents[0]


#SAVE MY MODEL
resourceSave = XMIResource(URI('a7.xmi'))
resourceSave.use_uuid = True

obj_copy = EcoreUtils.copyEObject(Se_Mod)
resourceSave.append(obj_copy)
resourceSave.append(Se_Mod)  # We add the root to the resource
resourceSave.save()  # will save the result in 'my/path.xmi'
resourceSave.save(output=URI('a7.xmi'))  # save the result in 'test/path.xmi'