import re
import sys


alias_dict={}
prgm_pt_dict={}
pst_pp=0
def WP_Simplification(wpinterpolant):
    wpinterpolant=wpinterpolant.replace("WPVar w32 ","").replace("w32 ","").replace("((","").replace(")))","))")
    wpinterpolant1=wpinterpolant.split(":")
    wpinterpolant_ex=""
    for parts in wpinterpolant1:
        parts_minute=parts.split(" ")
        xd=re.search("N[0-9]*", parts_minute[-1])
        if re.search("N[0-9]*", parts_minute[-1]):
            wpinterpolant_ex=wpinterpolant_ex+parts[0:len(parts)]            
        else:
            wpinterpolant_ex=wpinterpolant_ex+parts
        
    #print("********"+wpinterpolant_ex+"********\n")
    if ":" in wpinterpolant:
        key_list=[]
        values_list=[]
        pairs=wpinterpolant.split(":")
        for kys in pairs:
            key_list.append(kys.split(" ")[-1])
        for vals in pairs:
            values_list.append(vals.split(")")[0])
        for i1 in range(0, len(values_list)-1):
            alias_dict[key_list[i1]]=values_list[i1+1]
    
    cond_list=re.findall("Not.\([A-Z,a-z]* [0-9]* [_|A-Z,a-z][A-Z,a-z,0-9,_]*\)|Not.\([A-Z,a-z]* [_|A-Z,a-z][A-Z,a-z,0-9,_]* [_|A-Z,a-z][A-Z,a-z,0-9,_]*\)|\([A-Z,a-z]* [0-9]* [_|A-Z,a-z][A-Z,a-z,0-9,_]*\)|\([A-Z,a-z]* [_|A-Z,a-z][A-Z,a-z,0-9,_]* [_|A-Z,a-z][A-Z,a-z,0-9,_]*\)|\([A-Z,a-z]* [_|A-Z,a-z][A-Z,a-z,0-9,_]*\)", wpinterpolant_ex)
    final_pred=""
    #print("****---****"+str(cond_list)+"****---****\n")
    for cond in cond_list:
        if "Not (" in cond:
            condFmtlist=cond.replace("Not (","(").replace("(","").replace(")","").split(" ")

            if condFmtlist[1] in alias_dict and len(condFmtlist)==2:
                condFmtlist[1]=alias_dict[condFmtlist[1]]
            if  len(condFmtlist)==3: 
                if condFmtlist[2] in alias_dict:
                    condFmtlist[2]=alias_dict[condFmtlist[2]]
                
            if len(final_pred)==0:
                if len(condFmtlist)==2:
                    final_pred=final_pred+"Not("+condFmtlist[0]+" "+condFmtlist[1]+") "
                else:
                    final_pred=final_pred+"Not("+condFmtlist[2]+" "+condFmtlist[0]+" "+condFmtlist[1]+") "
            else:
                if len(condFmtlist)==2:
                    final_pred=final_pred+"And Not("+condFmtlist[0]+" "+condFmtlist[1]+") "
                else:
                    final_pred=final_pred+"And Not("+condFmtlist[2]+" "+condFmtlist[0]+" "+condFmtlist[1]+") "
        else:
            condFmtlist=cond.replace("(","").replace(")","").split(" ")

            if condFmtlist[1] in alias_dict and len(condFmtlist)==2:
                condFmtlist[1]=alias_dict[condFmtlist[1]]
            if len(condFmtlist)==3 and condFmtlist[2] in alias_dict:
                condFmtlist[2]=alias_dict[condFmtlist[2]]
                
            if len(final_pred)==0:
                if len(condFmtlist)==2:
                    final_pred=final_pred+"("+condFmtlist[0]+" "+condFmtlist[1]+") "
                else:
                    final_pred=final_pred+"("+condFmtlist[2]+" "+condFmtlist[0]+" "+condFmtlist[1]+") "
            else:
                if len(condFmtlist)==2:
                    final_pred=final_pred+"And ("+condFmtlist[0]+" "+condFmtlist[1]+") "
                else:
                    final_pred=final_pred+"And ("+condFmtlist[2]+" "+condFmtlist[0]+" "+condFmtlist[1]+") "
    return "Simplified::["+str(final_pred+"]")

InputFile1 = open(sys.argv[1], "r")
OutputFile1 = open("TX-FormattedOutput.txt", "w") 

setStack=0
setStartNodeVal=0
setGlobalStart=0
setGlobalAddressVal=0
setConValStart=0
setConAddress=0
setConContent=0
setConGlobal=0
setConLocal=0

prgmPtBlkId={}
pgrpt_name=0
for i in InputFile1:
#    print i
#==============================================================================
#     if "concretely-addressed store = [" in i and "]" not in i:
#         print i
#==============================================================================
    if ("warning: " in i or "KLEE:" in i) and "Subsumption Table Entry" not in i and "KLEE: done:" not in i and "KLEE: **********" not in i and "Storing entry for Node #1," not in i:
        continue
    elif " Location:" in i or "antecedent:" in i or "consequent:" in i or "." in i:
        continue
    elif "KLEE: Storing entry for Node #1," in i:
        setStartNodeVal=1
        continue
    elif "global = [creation depth:" in i:
        OutputFile1.write(i)
        setGlobalStart=1
    elif "content:" in i and len(i.strip())==8 and setGlobalStart==1:
        setGlobalAddressVal=1
        continue
    elif "function/value:" in i and setGlobalAddressVal==1:
        setGlobalAddressVal=0
        continue    
    elif "concretely-addressed store = [" in i and "]" not in i:
        setConValStart=1
        OutputFile1.write(i)
#==============================================================================
    elif "address:" in i and setConValStart==1:
         setConAddress=1
         continue
    elif "function/value:" in i and setConValStart==1 and setConAddress==1:# and setConContent==0:# and "@" in i:
         OutputFile1.write(i)
         setConAddress=0
         continue
#         setConContent=0
#==============================================================================
    elif "]" in i and len(i.strip())==1 and  setConValStart==1:
        setConValStart=0
        continue
    elif "function/value: i32" in i:
        continue
#==============================================================================
#     elif "function/value:" in i and setConValStart==1 and setConAddress==1 and "@" not in i:
#         OutputFile1.write(i)
#         setConLocal=1
#==============================================================================
    elif "content:" in i and len(i.strip())==8 and setConValStart==1:
        setConAddress=0
        setConValStart=0 
        setConContent=1
        continue
    elif "pointer to location object:" in i and "]" in i:
        OutputFile1.write("]\n")
        setGlobalStart=0        
    elif "KLEE: ********** Start of Program Point" in i:
#        print(i.split(":")[2])
        pgrpt_name=str(i.split(":")[2].split("Block")[0]).strip()
        newstate1="\n********** Block Label and Predecessor of Program Point:"+str(i.split(":")[2].split("Block")[0])+" **********\n";
        OutputFile1.write(newstate1)
        if setStartNodeVal==1:
            OutputFile1.write("\nThis is the start block (Node #1)")
            setStartNodeVal=0
            prgmPtBlkId[pgrpt_name]="(Node #1)"
    elif "; <label>:" in i and "; preds =" in i:
        newstate2=str(i.split("                         ")[0].split(";")[1])+str(i.split("                         ")[1])
#        print(newstate2)
        if pgrpt_name not in prgmPtBlkId:
            prgmPtBlkId[pgrpt_name]=i.split(";")[1].strip()
        OutputFile1.write(""+newstate2+"")
    elif "KLEE: *********************** End of Instructions ******************************************" in i:
        OutputFile1.write("*****************************************************************************")
    elif "warnings generated." in i:
        continue
    elif "oem" in i or len(i.strip()) ==1 and "]" not in i:
        continue
    elif "main(" in i or "^~~~" in i or "opt:" in i or "Using Z3 solver backend" in i:
        continue
    elif "stack: (empty)" in i or "offset:" in i or "address:" in i or "base:" in i or "concrete offset bound:" in i or "size:" in i:
        continue
    elif "content:" in i or " a right interpolant value:" in i or "branch infeasibility" in i :
        continue
    elif "pointer to location object:" in i and "]" not in i:
        continue
    elif "interpolant = (empty)" in i or "concretely-addressed store = []" in i or "symbolically-addressed store = []" in i or "concretely-addressed historical store = []" in i or "symbolically-addressed historical store = []" in i or "existentials =" in i:
        continue 
    elif "reason(s) for storage:" in i or "(ReadLSB" in i or ("stack:" in i and len(i.strip()) ==6):
        continue
    elif " !dbg" in i or "alloca i32" in i or "store " in i:
        continue
    elif "interpolant value:" in i:
        continue
    else:
        OutputFile1.write(i)

OutputFile1.close()

InputFile2 = open("TX-FormattedOutput.txt")
OutputFile2 = open("TX-ReadableFormattedOutput.txt", "w")  

countFV=0
wp=0
wp_string=""
for j in InputFile2:
    if "KLEE: ------------ Subsumption Table Entry ------------" in j:
        OutputFile2.write("------------ Subsumption Table Entry ------------\n")
    elif "global = [creation depth:" in j:
        OutputFile2.write("global = [\n")
    elif "Program point =" in j:
        pp_key=j.split("=")[1].strip()
#        print(pp_key)
        pst_pp=pp_key
        if pp_key not in prgm_pt_dict:
                prgm_pt_dict[pp_key]=[]
        OutputFile2.write(j)
    elif "function/value:" in j:
        countFV=countFV+1
        j=j.replace("function/value:","Variable:")
        j=j.split("=")[0]+"\n"
#==============================================================================
#         if (countFV%2==1):
#             j=j.replace("function/value:","Variable:")
#             j=j.split("=")[0]+"\n"
#         else:
#             continue
#==============================================================================
        OutputFile2.write(j)
    elif "wp interpolant = [true]" in j:
        OutputFile2.write(j)
        prgm_pt_dict[pst_pp].append(j.strip())
    elif "wp interpolant = [" in j and "]" in j:        
        k=WP_Simplification(j)
        OutputFile2.write(j)
        OutputFile2.write(k)
        prgm_pt_dict[pst_pp].append(k)
    elif "wp interpolant = [" in j and "]" not in j:
        wp=1
        wp_string=j.split("=")[1].strip()
        OutputFile2.write(j)
    elif wp==1 and "]" not in j:
        wp_string=wp_string+j.strip()
        OutputFile2.write(j)
    elif wp==1 and "]" in j:
        wp_string=wp_string+j.strip()
        OutputFile2.write(j)
        wp=0        
        OutputFile2.write("\nMerged: "+wp_string+"\n")
        sim_wp=    WP_Simplification(wp_string)
        OutputFile2.write("\n"+sim_wp+"\n")
#        print(pst_pp)
        prgm_pt_dict[pst_pp].append(sim_wp)
        wp_string=""                            
    else:
        OutputFile2.write(j)

OutputFile2.write("\n\n")
OutputFile2.write("===============================================================\n")
print("===============================================================")
print("List of Program points and their corresponding interpolants.")
OutputFile2.write("List of Program points and their corresponding interpolants.\n")
print("===============================================================")
OutputFile2.write("===============================================================\n")
for interpolant in prgm_pt_dict:
#==============================================================================
#     print(interpolant,prgm_pt_dict[interpolant])
#     print(type(prgm_pt_dict[interpolant]))
#==============================================================================
    print("Program Point: "+str(interpolant)+" has the following "+str(len(prgm_pt_dict[interpolant]))+" interpolant(s) and corresponding Block Identifier is "+str(prgmPtBlkId[interpolant]))
    OutputFile2.write("Program Point: "+str(interpolant)+" has the following "+str(len(prgm_pt_dict[interpolant]))+" interpolant(s):\n")
    if len(prgm_pt_dict[interpolant])==1:
        if "Simplified::" in prgm_pt_dict[interpolant][0]:
            print(prgm_pt_dict[interpolant][0].replace("Simplified::", "wp interpolant-1="))
            OutputFile2.write(prgm_pt_dict[interpolant][0].replace("Simplified::", "wp interpolant-1=")+"\n")
            print("---------------------------------------------------------------")
            OutputFile2.write("---------------------------------------------------------------\n")
        else:
            print(prgm_pt_dict[interpolant][0].replace("wp interpolant =", "wp interpolant-1="))
            OutputFile2.write(prgm_pt_dict[interpolant][0].replace("wp interpolant =", "wp interpolant-1=")+"\n")
            print("---------------------------------------------------------------")
            OutputFile2.write("---------------------------------------------------------------\n")
    else:
        for inter in range(0, len(prgm_pt_dict[interpolant])):
            if "Simplified::" in prgm_pt_dict[interpolant][inter]:
                print(prgm_pt_dict[interpolant][inter].replace("Simplified::", "wp interpolant-"+str(inter+1)+"="))
                OutputFile2.write(prgm_pt_dict[interpolant][inter].replace("Simplified::", "wp interpolant-"+str(inter+1)+"=")+"\n")
            else:
                print(prgm_pt_dict[interpolant][inter].replace("wp interpolant =",  "wp interpolant-"+str(inter+1)+"="))
                OutputFile2.write(prgm_pt_dict[interpolant][inter].replace("wp interpolant =",  "wp interpolant-"+str(inter+1)+"=")+"\n")
        print("---------------------------------------------------------------")
        OutputFile2.write("---------------------------------------------------------------\n")
        unique_interpolant=set(prgm_pt_dict[interpolant])
#        print(unique_interpolant)
        print("******************************************************************")
        OutputFile2.write("******************************************************************\n")
        print("The number of unique interpolants for program point: "+str(interpolant)+" is "+str(len(unique_interpolant)))
        OutputFile2.write("The number of unique interpolants for program point: "+str(interpolant)+" is "+str(len(unique_interpolant)))
        if len(unique_interpolant)!= len(prgm_pt_dict[interpolant]):
                print("The Unique Interpolants are:")
                OutputFile2.write("The Unique Interpolants are:\n")
                uni_index=0
                for uni_inter in unique_interpolant:
                            uni_index=uni_index+1
                            if "Simplified::" in uni_inter:
                                print(uni_inter.replace("Simplified::", "wp interpolant-"+str(uni_index)+"="))
                                OutputFile2.write(uni_inter.replace("Simplified::", "wp interpolant-"+str(uni_index)+"=")+"\n")
                            else:
                                print(uni_inter.replace("wp interpolant =",  "wp interpolant-"+str(uni_index)+"="))
                                OutputFile2.write(uni_inter.replace("wp interpolant =",  "wp interpolant-"+str(uni_index)+"=")+"\n")
        print("******************************************************************")
        OutputFile2.write("******************************************************************\n")
        OutputFile2.write("******************************************************************\n")


print(prgmPtBlkId)           