#!/usr/bin/env python

# shift-apple-T  ==> toggle fold
####################################################################
# Compares target and produced syllables to determine the error type.
###################################################################

import optparse # deprecated; use argparse
import csv
import os, glob
#import fileinput, sys # for replaceAll(....)


class bcolors:  # colors for testing
    """ Defines colors for debug printing. """
    MAGENTA = '\033[95m'; BLUE = '\033[94m'; GREEN = '\033[92m'; YELLOW='\033[93m';
    RED = '\033[91m';  CYAN= '\033[96m'; 
    ENDC = '\033[0m';
    #GRAY= '\033[90m'; 
    def disable(self):
        self.GRAY=self.PURPLE=self.CYAN=self.MAGENTA= self.BLUE = self.GREEN = self.RED = self.YELLOW=self.ENDC= ''


def dprint(print_str,color_str):
    """ print colored statements for debugging

        print_str -- string to print
        color_str -- name of color, e.g. BLUE, GREEN, etc
    """
    if color_str == "blue": print bcolors.BLUE+print_str+bcolors.ENDC
    elif color_str == "red": print bcolors.RED+print_str+bcolors.ENDC
    elif color_str == "magenta": print bcolors.MAGENTA+print_str+bcolors.ENDC
    elif color_str == "green": print bcolors.GREEN+print_str+bcolors.ENDC
    #elif color_str == "gray": print bcolors.GRAY+print_str+bcolors.ENDC   # don't use, too light on white background
    elif color_str == "purple": print bcolors.PURPLE+print_str+bcolors.ENDC
    elif color_str == "cyan": print bcolors.CYAN+print_str+bcolors.ENDC
    #elif color_str == "yellow": print bcolors.YELLOW+print_str+bcolors.ENDC  # don't use, too light on white background
    else: print color_str

#
#
#
def get_syll_parts(syll_string):
    """ Take syllable string and determine which parts are onset, vowel, coda"""

    vowels = "aeiouE@"
    for vowel in vowels:
        if vowel in syll_string:
#            index = syll_string.index(vowel) # only expecting one (lowercase) vowel
	    """reversing to search from right to left, because most epenthesis errors
are in the onset...so if you keep saying that it's that first vowel
that's the nucleus, you'll incorrectly determine that there's a
cons-deletion error in the onset and some kind of "other" error in the
coda. (think: drevd>derevd.if you were to decide that the onset is 'd',
and the coda is 'revd'	"""
	    index = syll_string.rindex(vowel)# no
	    onset,vowel_nucleus,coda = syll_string[:index], syll_string[index],syll_string[index+1:]
            return([onset,vowel_nucleus,coda])

    else: # there is no vowel nucleus; most likely this is just a production like "sk" or "s"
        onset = syll_string
        vowel_nucleus=""
        coda = ""
        return([onset,vowel_nucleus,coda])


#
def compare_parts(syll_part,target_part,prod_part,set_num,other_target_part):
    """ Take (target,produced) pair of onsets and compare to determine error type;
        Also takes the set number, in order to determine if an s+C error is legal or illegal if the control_flag is on
        Returns [[[[[[[[[ right now ]]]]]]]]] str describing the error 

        other_target_part would be the onset if target_part is coda and vice versa"""

    """#  NOTE: special cases haven't implemented yet
        #
        #  (1) may get errors like:  skest > skevd,skest
        #       that means that they produced TWO things
        #     ****************************  so watch for "," in produced.   *********************************** !!!!!!!
        #           in the case above, see how skest WAS produced correctly finally, so for my purposes here the above is basically the same as skest > skevd
        #                   the only thing that woud differ is that WOULD NEED TO INCREMENT THE NUMBER OF SYLLABLES PRODUCED/ATTEMPTED.
        #           in the case of something liek:  skest > skevd, skerk:
        #                   also would need to increment the number of syll produced, but also:
        #                               note that would have like 2  things to check:  skest>skevd AND skest > skerk
        #  (2) more than one vowel in nucleus
        #  (3) dj is actually a d before an r, but r is left out...  = palatalized???
        #
        #  (4 - ...)  so basically keep going through output and look at diff types of errors.. probly won't care about any of
        #  those for this 10/14 prog report though!!!!!!!!!!!
        ###################################################################
    """

    if testing_flag: dprint("\n\n~~~~~~~~~~~~~~~~~~~~~~ starting COMPARE_PARTS ~~~~~~~~~~~~~~~~~~~~~~ ", "blue")
    stimuli_cons = "g,v,t,l,d,r,s,k"
    controlled_sets = [1, 2, 5, 11, 12, 14, 17, 18, 19, 20, 21, 23, 24, 25, 27, 30, 32, 34, 36, 40, 41, 43, 45, 47, 50, 51, 53, 56, 58, 59, 61, 63]

####################  debugging ####################################################################################
    # Are we looking at sk/st and the control flag is set? 
    if control_flag:
        dprint("........... control_flag ON, so redefining onset_clusters and coda_clusters ........", "red")
        onset_clusters = "gv","tl","dr","st"
        coda_clusters = "vd","rk","lg","sk"
    else: 
        dprint("........... control_flag OFF, so back to orig onset_clusters and coda_clusters ........", "green")
        onset_clusters = "gv","tl","dr","sk"
        coda_clusters = "vd","rk","lg","st"

    if control_flag and (prod_part == "st" or prod_part == "sk") and (set_num in controlled_sets):
        dprint("\t......... prod_part = st or prod_part = sk and set_num is controlled (so then actually target MUST be 'sk' and prod MUST be 'st' -- for codas)","red")
        dprint("\t\tset_num is "+str(set_num), "red")
        dprint("\t\tsyll_part: "+syll_part+", target_part: "+target_part+", prod_part: "+prod_part, "red")

    if (not control_flag) and (prod_part == "st" or prod_part == "sk") and (set_num in controlled_sets):
        dprint("\t......... prod_part = st or prod_part = sk and set_num is NOT controlled ..........","green")
        dprint("\t\tset_num is "+str(set_num), "green")
        dprint("\t\tsyll_part: "+syll_part+", target_part: "+target_part+", prod_part: "+prod_part, "green")
####################  END debugging ####################################################################################

        """ maybe better explanation of test cases than the above (these are also in a fake test file .csv)
######### if looking at a CONTROLLED sequence:  
# EX: misproduced: stVCC 
#   if control_flag = NOT set:  illegal move (st)        
#   if control_flag = SET:      legal move (st)       
# EX: misproduced: skVCC 
#   if control_flag = NOT set:  legal move (sk)        
#   if control_flag = SET:      illegal move (sk)       
# EX: misproduced: CCVst 
#   if control_flag = NOT set:  legal move (st)        
#   if control_flag = SET:      illegal move (st)       
# EX: misproduced: CCVsk 
#   if control_flag = NOT set:  illegal move (sk)        
#   if control_flag = SET:      legal move (sk)       
# 
########## if looking at a NON-cntrl=EXPER sequence:  
# EX: misproduced: stVCC 
#   if control_flag = NOT set:  illegal move (st)        
#   if control_flag = SET:      ilegal move (st)       
# EX: misproduced: skVCC 
#   if control_flag = NOT set:  legal move (sk)        
#   if control_flag = SET:      legal move (sk)       
# EX: misproduced: CCVst 
#   if control_flag = NOT set:  legal move (st)        
#   if control_flag = SET:      legal move (st)       
# EX: misproduced: CCVsk 
#   if control_flag = NOT set:  illegal move (sk)        
#   if control_flag = SET:      illegal move (sk)    


        """




    ###############################################################################################
    # comparing ONSETS
    ################################################################################################
    if testing_flag: dprint("\t~~~~~~~~~~~~~~~~~~~~~~ comparing ONSETS ~~~~~~~~~~~~~~~~~~~~~~", "blue")
    if syll_part == "onset":
        onset_error_type = "__undetermined before onset comparison__"
        target_onset = target_part
        prod_onset = prod_part
        target_coda = other_target_part
        if ((prod_onset=="st" or prod_onset == "sk") and (int(set_num) in controlled_sets)): 
            if control_flag: 
                if testing_flag: dprint("\tDETERMINED THAT prod_ONSET IS st OR sk; AND THIS IS A CONTROLLED SET","red")
                if testing_flag: dprint("\t\tset_num, target_onset, prod_onset, target_coda: "+str(set_num)+", "+target_onset+", "+prod_onset+", "+target_coda,"red")
            else:
                if testing_flag: dprint("\tDETERMINED THAT prod_ONSET IS st OR sk; AND THIS IS A CONTROLLED SET..............  (but don't care because the control flag is off)","cyan")

         # if just 1 consonant:
        if len(prod_onset) == 1:
            if prod_onset in target_onset:   # e.g. produced = "gest," target = "gvest", so is "g" in "gv"
               onset_error_type = "CLUSTER_REPAIR-CONS_DELETION"
            elif prod_onset in stimuli_cons: # e.g. prod = "lest," target = "gvest"; i.e. the prod onset is a cons that's not in the target onset, but IS in the set of consonants used in the stimuli
               onset_error_type = "CLUSTER_REPAIR-INSERT_CONS_IN_INPUT_BUT_NOT_IN_TARGET_CLUSTER (but I don't like that it says INSERT!!  REPLACE is much better)"
            else: # if prod_onset NOT in stimuli_cons; e.g. prod = "mest," target = "gvest"
               onset_error_type = "OTHER: a cons/char not in stimuli cons replaces onset cluster"

        elif len(prod_onset) == 2:
            if prod_onset in onset_clusters: 
                onset_error_type="WHOLE_CLUSTER_MV_LEGAL"
            elif prod_onset in coda_clusters: 
                onset_error_type="WHOLE_CLUSTER_MV_ILLEGAL"
            elif prod_onset[0] in stimuli_cons and prod_onset[1] in stimuli_cons:  #2-cons cluster in onset, but not one that is in my set of onset clusters; but BOTH cons do appear in set of cons
                onset_error_type = "OTHER - NEW CLUSTER IN ONSET: both cons appear in set of cons, but not together in a cluster"
            #if one of the cons in produced onset is in the target onset
            elif prod_onset[0] in target_onset and prod_onset[1] in stimuli_cons:
                onset_error_type = "OTHER - NEW CLUSTER IN ONSET: 1st cons is in target cluster; the 2nd IS in the set of cons"
            elif prod_onset[0] in target_onset and (not prod_onset[1] in stimuli_cons):
                onset_error_type = "OTHER - NEW CLUSTER IN ONSET: 1st cons is in target cluster; the 2nd is NOTin the set of cons"
            elif prod_onset[1] in target_onset and prod_onset[0] in stimuli_cons:
                onset_error_type = "OTHER - NEW CLUSTER IN ONSET: 2nd cons is in target cluster; the 1st IS in the set of cons"
            elif prod_onset[1] in target_onset and (not prod_onset[0] in stimuli_cons):
                onset_error_type = "OTHER - NEW CLUSTER IN ONSET: 2nd cons is in target cluster; the 1st is NOT in the set of cons"
            else: #there's a 2-cons cluster in onset, but not one that appears in my set of onset clusters and NEITHER cons should appear in set of cons
                onset_error_type = "OTHER - NEW CLUSTER IN ONSET: neither cons in new onset cluster is in the set of cons"


        # for now, the definition of cluster repair is limited to: (1) vowel epenthesis and (2) cons deletion. So if a produced
        #   onset or coda has exactly 3 characters, check if first char plus last char are the cons in the target cluster, and
        #   if the middle one is a vowel or @ -- if vowel epenthesis is happening.
        elif len(prod_onset) == 3:
            if target_onset in prod_onset and ("-" not in prod_onset):
                onset_error_type = "OTHER: produced onset contains target onset + some other char, but not '-'"
            # now checking to see if actually there was movement so need target CODA!
            elif target_coda in prod_onset:   # don't need this, I think, because did the onset_clusters/coda_clusters re-assignment
                onset_error_type = "ILLEGAL MOVEMENT: produced onset contains target CODA +  one other char"
            elif prod_onset[1] in "aeiouAEIOU@" and prod_onset[0]==target_onset[0] and prod_onset[2]==target_onset[1]:
                onset_error_type = "CLUSTER_REPAIR-VOWEL_EPENTHESIS"
            elif prod_onset[1] == "-" and prod_onset[0]==target_onset[0] and prod_onset[2]==target_onset[1]:
                onset_error_type = "CUT-OFF (temp classif.): 1st and 3rd char are in set of stimuli cons; middle char is '-'"
            elif "-" in prod_onset:
                onset_error_type = "CUT-OFF (temp classif.): some kind of cut-off error in onset"
            else: # not straight-up vowel epenthesis
                onset_error_type = "OTHER: NEW_ONSET_CLUSTER_HAS_3_CHAR"
        
        elif len(prod_onset) > 3:
            if target_onset in prod_onset and ("-" not in prod_onset):
                onset_error_type = "OTHER: produced onset contains target onset + some other chars, but not '-'"
            # now checking to see if actually there was movement so need target ONSET!
            elif target_coda in prod_onset: 
                onset_error_type = "ILLEGAL MOVEMENT: produced onset contains target CODA + some other chars"
            else:
                onset_error_type = "OTHER: NEW_ONSET_CLUSTER_HAS_MORE_THAN_3_CHAR"

            # should not happen... esp if prod_onset is "", but that should not have been passed in ??:
        else: 
            onset_error_type = "****** compare_parts() found no errors ******* ??? or haven't implemented... ??  [this should not be printing. should not happen according to the conditional logic here... esp if prod_onset is "", but that should not have been passed in ??]"

        return onset_error_type

    ################################################################################################################
    # comparing CODAS
    ################################################################################################################
    if testing_flag: dprint("\t~~~~~~~~~~~~~~~~~~~~~~ comparing CODAS ~~~~~~~~~~~~~~~~~~~~~~", "blue")
    if syll_part == "coda":
        coda_error_type = "__undetermined before coda comparison__"
        target_coda = target_part
        prod_coda= prod_part
        target_onset = other_target_part
        if ((prod_coda=="st" or prod_coda == "sk") and (int(set_num) in controlled_sets)): 
            if control_flag: 
                if testing_flag: dprint("\tDETERMINED THAT prod_CODA IS st OR sk; AND THIS IS A CONTROLLED SET", "red")
                if testing_flag: dprint("\t\tset_num, target_coda (should be sk), prod_coda (should be st), target_onset: "+str(set_num)+", "+target_coda+", "+prod_coda+", "+target_onset,"red")
            else:
                if testing_flag: dprint("\tDETERMINED THAT prod_CODA IS st OR sk; AND THIS IS A CONTROLLED SET..............  (but don't care because the control flag is off)","cyan")


         # if just 1 consonant:
        if len(prod_coda) == 1:
            if prod_coda in target_coda:   # e.g. produced = "gves," target = "gvesk", so is "s" in "sk"
               coda_error_type = "CLUSTER_REPAIR-CONS_DELETION"
            elif prod_coda in stimuli_cons: # is prod coda in the set of stimuli consonants? e.g. if "gvesk">"gvel", is "" in any of the 8 cons
               coda_error_type = "CLUSTER_REPAIR-INSERT_CONS_IN_INPUT_BUT_NOT_IN_TARGET_CLUSTER (but I don't like INSERT!!  REPLACE is much better)"
            else: # if prod_coda NOT in stimuli_cons; e.g. prod = "mest," target = "gvest"
               coda_error_type = "OTHER: a cons/char not in stimuli cons replaces coda cluster"

        elif len(prod_coda) == 2:
            if prod_coda in coda_clusters: 
                coda_error_type="WHOLE_CLUSTER_MV_LEGAL"
            elif prod_coda in onset_clusters: 
                coda_error_type="WHOLE_CLUSTER_MV_ILLEGAL"
            elif (prod_coda[0] == target_coda[0] ) and (prod_coda[1] == "?"):
                coda_error_type = "OTHER: 2nd cons of target_cluster is glottal stop"
            elif prod_coda[0] in stimuli_cons and prod_coda[1] in stimuli_cons:  #2-cons cluster in coda, but not one that is in my set of coda clusters; but BOTH cons do appear in set of cons
                coda_error_type = "OTHER - NEW CLUSTER IN CODA: both cons appear in set of cons, but not together in a cluster"
              #if one of the cons in produced coda is in the target coda
            elif prod_coda[0] in target_coda and prod_coda[1] in stimuli_cons:
                coda_error_type = "OTHER - NEW CLUSTER IN CODA: 1st cons is in target cluster; the 2nd IS in the set of cons"
            elif prod_coda[0] in target_coda and (not prod_coda[1] in stimuli_cons):
                coda_error_type = "OTHER - NEW CLUSTER IN CODA: 1st cons is in target cluster; the 2nd is NOTin the set of cons"
            elif prod_coda[1] in target_coda and prod_coda[0] in stimuli_cons:
                coda_error_type = "OTHER - NEW CLUSTER IN CODA: 2nd cons is in target cluster; the 1st IS in the set of cons"
            elif prod_coda[1] in target_coda and (not prod_coda[0] in stimuli_cons):
                coda_error_type = "OTHER - NEW CLUSTER IN CODA: 2nd cons is in target cluster; the 1st is NOT in the set of cons"
            else: #there's a 2-cons cluster in coda, but not one that appears in my set of coda clusters and NEITHER cons should appear in set of cons
            # but if there are 2 consonants and exactly 1 CONS UNCHANGED AND 2nd CONS *IS NOT* IN INPUT:  is that also called cons exchange?????????????????????
                coda_error_type = "OTHER - NEW CLUSTER IN CODA: neither cons in new coda cluster is in the set of cons"


        # for now, the definition of cluster repair is limited to: (1) vowel epenthesis and (2) cons deletion. So if a produced
        #   onset or coda has exactly 3 characters, check if first char plus last char are the cons in the target cluster, and
        #   if the middle one is a vowel or @ -- if vowel epenthesis is happening.
        elif len(prod_coda) == 3:
            if target_coda in prod_coda: 
                onset_error_type = "OTHER: produced coda contains target coda + some other char, which may be '-'"
            # now checking to see if actually there was movement so need target ONSET!
            elif target_onset in prod_coda: 
                coda_error_type = "ILLEGAL MOVEMENT: produced coda contains target ONSET + one other char"
            elif prod_coda[1] in "aeiouAEIOU@" and prod_coda[0]==target_coda[0] and prod_coda[2]==target_coda[1]:
                coda_error_type = "CLUSTER_REPAIR-VOWEL_EPENTHESIS"
            elif "-" in prod_coda:
                coda_error_type = "CUT-OFF (temp classif.): some kind of cut-off error in coda"
            else: # not straight-up vowel epenthesis
                coda_error_type = "OTHER: NEW_CODA_CLUSTER_HAS_3_CHAR"
        
        elif len(prod_coda) > 3:
            if target_coda in prod_coda: 
                coda_error_type = "OTHER: produced coda contains target coda + some other chars"
            # now checking to see if actually there was movement so need target ONSET!
            elif target_onset in prod_coda: 
                coda_error_type = "ILLEGAL MOVEMENT: produced coda contains target ONSET+ some other chars"
            else: 
                coda_error_type = "coda longer than 3 char.........  yet to classify; temp: NEW_CODA_CLUSTER_HAS_MORE_THAN_3_CHAR"

        # should not happen:
        else: 
            coda_error_type = "****** compare_parts() found no errors ******* or it's one of the ones in the notes above that haven't implemented yet.  [should not be printing.  should not happen... esp if prod_onset is "", but that should not have been passed in ??]"

        return coda_error_type



    ################################################################################################################
    # comparing some other part
    ################################################################################################################
    else: # syll_part neither "onset" nor "coda"
        error_type = "UMMMMMMMMMMMMMMMMMMMMMMM   syll_part flag neither onset or coda, wanna try that again? "
        return error_type

#
def writeCSV(subj_id,all_errors):
    """ About the files that are created (FIXXXXXXXXXXXMEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE 2 csv files and 1 txt file with general comments) CREATED by det_error_types.py:

        Composed of two main parts:
           (1) table mapping types of mistakes with their frequencies
               (so this one remains to be implemented)
           (2) lines like this:
                very specific error type, syll_identifier (ex: set96seq4syll3), target syll, produced syll, target cluster, produced cluster, comment
                       [comment part not implemented yet]

           (3) general comments from the input form php
    """


    # variables in this def
    frequencies_table = {}  # map error type to how many times it occurred.... NOTE,update:   changing table layout
    errors_table = {}     # dict indexed on index number;
                            # cols - syll id, target syll, produced syll, target cluster, produced cluster(,comment)
    general_comments = "NOT IMPLEMENTED YET"   # general comments part [see (3) above] not implemented yet, so string stays empty for now
    #all_error_types = ""
    legal_syll_produced = {}   # id all produced CCVCC syllables that actually appear in the stimuli (to prove instances != syllables)


########  wait a minute, should OTHER include OMIT and ? ..........   I think don't do that!  go back and don't change those to OTHER
    # add up frequencies for each type of mistake
    cluster_plus_broad_error_type = "** undetermined **"
    for e in all_errors:	# the following determines e["involved cluster"]
        if e["very broad error type"]  == "WHOLE_CLUSTER_MV_LEGAL":
            e["involved cluster"] = e["prod cluster"]+ "_"
            #print "$"*300; print e; print involved_cluster; print "@@@@@@@@@@@@@@@@@@@<<<<<<<<<<<<<";print e["error type"]; print "<<<<<<<<<<<<<"
        elif e["very broad error type"]  == "WHOLE_CLUSTER_MV_ILLEGAL":
            e["involved cluster"] = e["prod cluster"]+ "_"
        elif e["very broad error type"]==("CLUSTER_REPAIR-CONS_DELETION"):
            e["involved cluster"] = e["target cluster"]+"_"
        elif e["very broad error type"]==("CLUSTER_REPAIR-VOWEL_EPENTHESIS"):
            e["involved cluster"] = e["target cluster"]+"_"
        else:
	    e["involved cluster"] = ""

        #add the produced cluster for mv errors, the target cluster if cluster repair error
        cluster_plus_broad_area_type = e["involved cluster"] + e["very broad error type"]     # doing this merging of strings/fields
                                                                         #thing because i want to be able to just easily sort on a column in a spreadsheet
        if cluster_plus_broad_area_type in frequencies_table.keys():
            frequencies_table[cluster_plus_broad_area_type]+=1  # increment frequency count of this error type
        else:
            frequencies_table[cluster_plus_broad_area_type] = 1

    if testing_flag: 
        output_dir_just_freq_table = "TESTING_from_detErrors_to_gnuPlotting-just_frequencies_tables/"
        output_dir_all_but_freq_table = "TESTING_from_detErrors-all_but_frequencies_table/"
    else: 
        output_dir_just_freq_table = "from_detErrors_to_gnuPlotting-just_frequencies_tables/"
        output_dir_all_but_freq_table = "from_detErrors-all_but_frequencies_table/"


    # write file with frequencies of broad error types for each cluster
    outputCSVfreq=open(output_dir_all_but_freq_table+subj_id+"_bad_old_freq_table.csv","w")
    outputCSVfreq.write("cluster plus broad error type, frequency\n") #write headers
    keys = frequencies_table.keys()
    keys.sort()
    keys.reverse()
    for cluster_plus_broad_error_type in keys:
        outputCSVfreq.write(cluster_plus_broad_error_type+","+str(frequencies_table[cluster_plus_broad_error_type])+"\n")


    outputCSVfreq.close()

    ############################  note changing table layout (but writing to a subjxx_frequencies_table2.csv,
    ###### not replacing the old one....  also need the involved cluster crap above
    # I want the columns to be the different error types.
    all_cl = ["gv","tl","dr","sk","vd","lg","rk","st"]
    broad_error_types = ["WHOLE_CLUSTER_MV_LEGAL","WHOLE_CLUSTER_MV_ILLEGAL","CLUSTER_REPAIR-CONS_DELETION","CLUSTER_REPAIR-VOWEL_EPENTHESIS","OTHER"]
    ft2 = {}  # freq table 2
    # initialize
    for cl in all_cl:
        ft2[cl]={}
        for b in broad_error_types:
            ft2[cl].update({b:0})
      #      dprint("just put in "+b+" and "+cl,"blue")
    for e in all_errors:
        icl= e["involved cluster"].split("_")[0]
        for cl in all_cl:
            for b in broad_error_types:
                if (icl==cl and e["very broad error type"]==b): ft2[cl][b] += 1


    # write file with frequencies of broad error types for each cluster
    outputCSVfreq2=open(output_dir_just_freq_table+subj_id+"_frequencies_table.csv","w")
    outputCSVfreq2.write("CLUSTER,WHOLE_CLUSTER_MV_LEGAL,WHOLE_CLUSTER_MV_ILLEGAL,CLUSTER_REPAIR-CONS_DELETION,CLUSTER_REPAIR-VOWEL_EPENTHESIS,OTHER\n") # write headers
    for cl in all_cl:
        s = cl
        for b in broad_error_types:
         #   dprint(str(ft2[cl][b]),"red")
            s =s + ","+str(ft2[cl][b])
        #outputCSVfreq2.write(cl+","+    ",".join(str(i) for i in ft2[cl].values()   )+"\n")
        outputCSVfreq2.write(s+"\n")
    outputCSVfreq2.close()

    # write file with very specific error types for each cluster and other infoz
    outputCSVall = open(output_dir_all_but_freq_table+subj_id+"_all_errors_table.csv","w")
    outputCSVall.write("very specific error type, syll id, syll, target cluster,prod cluster\n") #write headers
    for e in all_errors:
        #dprint(e["syll id"]+"; "+e["very broad error type"],"green")
        #print(str(e))
        outputCSVall.write(e["very specific error type"]  +","    +e["syll id"]                   +","    +e["syll"]                      +","    +e["target cluster"]            +","    +e["prod cluster"]              +"\n")
        # note e["syll"] is actually "targetsyll>prodsyll" string
    outputCSVall.close()

    # get notes (from top of coding_form) and write to separate file
    outputTXTcomments = open(output_dir_all_but_freq_table+subj_id+"_general_comments.txt","w")
    outputTXTcomments.write(general_comments)
    outputTXTcomments.close()

    # id all produced CCVCC syllables that actually appear in the stimuli (to prove instances != syllables)
    #   and write to file
    outputCSVlegals = open(output_dir_all_but_freq_table+subj_id+"_legal_CCVCC.csv","w")
    legal_syll_stimuli =["skerk","skelg","skevd","skest","drerk","drelg","drevd","drest","gverk","gvelg","gvevd","gvest","lerk","tlelg","tlevd","tlest"]
    for e in all_errors:
        prod_syll = e["syll"][-5:]  # e["syll"][-5:] because there's no e["target syll"]; it just looks like this "targ > prod"
        #dprint("prod_syll: "+prod_syll, "red")
        #dprint("e[syll]: "+e["syll"], "blue")
        if prod_syll in legal_syll_stimuli:
            if prod_syll in legal_syll_produced.keys():
              #  dprint("prod_syll if in legal stim: "+prod_syll, "red")
                legal_syll_produced[prod_syll] +=1
            else:
              #  dprint("adding new prod_syll: "+prod_syll, "blue")
                legal_syll_produced[prod_syll] =1

    outputCSVlegals.write("syll,freq\n") #write headers
    # list comprehension!
    #[outputCSVlegals.write(syll+","+legal_syll_produced[syll]+"\n") for syll in legal_syll_produced]
    for syll in legal_syll_produced:
        outputCSVlegals.write(syll+","+str(legal_syll_produced[syll])+"\n")
    outputCSVlegals.write("\ntotal: "+str(sum(legal_syll_produced.values()))+"\n")  # how many legal syllables produced in all
    outputCSVlegals.close()



#
def read_in_errors_from_CSV_file():
    #inputCSVerrors = open(args[1]) # list of target,produced pairs of syll
    inputCSVerrors = open(infile) # list of target,produced pairs of syll
    global error_pairs_list # yes, globals. because doing all the crazy modularizing.
    error_pairs_list = inputCSVerrors.readlines()[1:] # skip header row
    inputCSVerrors.close()
#
# outputting all the results and diffing (i.e. unit testing, sorta) and the results of the diffing..
def write_results_and_diffs():
    print "Number syllables attempted: " +str( total_num_attempted)
    print "Incorrect syllables: " + str(syll_count)
    print "All errors: " + str(error_count)

    """  how to test:

    with just INPUTS/subj03.csv for now
    to name, pass in: "03"
    ./det_error_types_v2.py 03 INPUTS/subj03.csv

    then diff with

    output everything to curr dir
    will have:
	03_legal_CCVCC.csv
	03_general_comments.txt
	03_frequencies_table.csv
	03_bad_old_frequencies_table.csv
	03_all_errors_table.csv


    THEN DIFF with same crap in older_outs/outs-for_prog_report/
    in fact, just do it in main
    output results to something"""
    """print "*"*10+" diffing "+"*"*10+" results from INPUTS/subj03.csv results vs old results in outs-for_prog_reports):"
    outputDIFFfile = open("diff_results_subj_3.txt","w")
    outputDIFFfile.write("result of os.system('diff '+file_name_to_diff+'older_outs/outs-for_prog_report/'+file_name_to_diff)")
    outputDIFFfile.close()
    for file_name_to_diff in ["03_legal_CCVCC.csv","03_general_comments.txt","03_frequencies_table.csv","03_bad_old_frequencies_table.csv","03_all_errors_table.csv"]:
	print ". . . . comparing "+file_name_to_diff+"'s . . ."

	#These ones  BREAKS SHIT, MAKE HUGE FILE/TAKE UP SWAP SPACE, DO NOT RUN IT. THE CAT THING BREAKS OR SOMETHING.
	#os.system("diff "+file_name_to_diff+" older_outs/outs-for_prog_report/"+file_name_to_diff+" > result")
	#os.system("cat diff_results_subj_3 result > diff_results_subj_3")

	os.system("diff "+file_name_to_diff+" older_outs/outs-for_prog_report/"+file_name_to_diff)

    print("**********  ls -alphG (must = 99B) *************"); os.system("ls -alphG diff_results_subj_3")
    print("**********  tail'ing it: *************"); os.system("tail diff_results_subj_3")
    print "*"*10+" done diffing "+"*"*30
    """
#
#
#
def main():
        #############################################################################
    # show_usage_infoz_and_do_arg_things: 

    # configure the option parser (run this file with -h option to see the usage)
    # 1st arg is name of this subject for dir naming, etc;
    # 2nd arg is the csv file with syllable id, target syll, prod syll
    usage = "usage: %prog name_of_dir_with_nknet_CSVs controlFlag testingFlag (controlFlag, testingFlag  should be 0 or 1) [[!!!  because of the way I'm specifying flags right now, the dir of CSV's must hold all the same type files, e.g. ALL controls or ALL experimental]"
    parser = optparse.OptionParser(usage)
    global args # yes, globals. because doing all the crazy modularizing.
    (options,args) = parser.parse_args()
    if len(args) != 3: 
        parser.error(usage)
    global control_flag
    control_flag = int(args[1]) 
    dprint("=>   control flag is "+str(control_flag), "blue")
    global testing_flag
    testing_flag = int(args[2]) 
    dprint("=>   testing flag is "+str(testing_flag), "blue")

    dir_of_CSVs = args[0]

    #############################################################################
    # For each CSV file (fresh from nk.net), do stuff
    #############################################################################
    #for infile in glob.glob(os.path.join(dir, '*.csv') ): 
    global infile
    global subj_id
    for infile in glob.glob(os.path.join(dir_of_CSVs, '*.csv') ):
        # rename with same thing as the csv that was passed in
        subj_id=os.path.splitext(os.path.basename(infile))[0]   #Returns the final component of a pathname, minus the ext
        #subj_id=os.path.splitext(os.path.basename(args[0]))[0]   #Returns the final component of a pathname, minus the ext
        #dprint("OK, here's the new thing to name stuff: "+subj_id, "blue")
        dprint("\n=========> current_infile and subj_id: "+infile+", "+subj_id, "blue")


        """   ###############
        #
        #
        #   note! change stuff here....
#  (1)   ====> now that i'm thinking of it, the easiest way to do batch crap for det_errors.py is just to wrap what's already there in a new thing that browses passed in dir for all files that start with:
#	from_nknet_to_detErrors_subj*
#
#

    """

        # >>>>>>>> defining the crazy globals >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
       # set total num *attempted* syll to total num syll in the stimuli (just for stats at the end, for now)
        global total_num_attempted; total_num_attempted = 96*4*3
        global error_count; error_count = 0 # why was this set to 1 before???
        # syll_count should be <= error_count, assuming sometimes there would be more than 1 error per syllable pair
        global syll_count; syll_count = 0
        # <<<<<<<<<<<<<<<< defining the crazy globals <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        all_errors = []
        error_type = "__undetermined__" # default

    ####################################################################
    #  YES I KNOW I'M GOING OVERBOARD WITH THE MODULARIZING, BUT NEED IT FOR NOW.
    ####################################################################

    
        read_in_errors_from_CSV_file()

        for error_pair in error_pairs_list:	    # grab each target syllable and produced syllable and do stuff with them to get error_type, other features
            error_pair = error_pair.strip()
            if error_pair and error_pair[0]!="#": # ignore (parts of) lines beginning with hashes
        # The input csv file should have lines like this: syll_identifier (ex: set96seq4syll3), target syll, produced syll
                syll_id,target_syll,prod_syll = error_pair.split(",")[0:3]
                prod_syll = prod_syll.split("#")[0].strip() # ignore comment part  # but still keeping after the comment? what??????
                set_num = int(syll_id[3:5])
            
            #print "\tTARG/PROD: ", target_syll,",",prod_syll
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            # if target syll unintelligible or omitted, know the error type already
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                print("");print("looking at set:  "+str(set_num)+" -- "+error_pair+" ----------------------------------------------------------------------->")
                if testing_flag: dprint("prod_syll = "+prod_syll,"magenta")
                if prod_syll == '?' or prod_syll == 'OMIT' or prod_syll == "UNINTELLIGIBLE" or prod_syll == "---":
                    if testing_flag: dprint(" OK SO NOW IN HERE prod_syll = "+prod_syll,"magenta")
                # note: right now NOT counting the uintelligible syll in the total num of produced syllables!! So "OMIT" means either the subject skipped the syllable or I am omitting these from the data. but I am putting them in the charts as separate things now, just to see how much of a worry they really are.
                    total_num_attempted -= 1
                #syll_count -=1
                    if prod_syll=='?': 
                        error_type="UNINTELLIGIBLE... BUT CAREFUL!!  IN CODE, THIS IS BASED ON '?', BUT THAT MEANS GLOTTAL STOP TOO!"
                    elif prod_syll=='UNINTELLIGIBLE': 
                        error_type = "UNINTELLIGIBLE"
                    elif prod_syll==("OMIT" or "---"): 
                        error_type = "OMIT"
                    
                    error = {} # reset
                    error["syll id"] = syll_id
                    error["error count"] = "n/a" #OMIT and UNINTELLIGIBLE are not errors, so do not add to error count; but DO subtract OMITted ones from total num of attempted syll)" # not really errors! so not counting these.
                    error["error type"] = error_type
                    error["syll part"] = "n/a"
                    error["syll"] = target_syll+" > " + prod_syll
                    error["syll count"] = syll_count
                    error["target cluster"] = error["prod cluster"] = "n/a"
                    all_errors.append(error)
                    #<<<<<<<<<<<<<<<<<<  end error type ? or OMIT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                else:
                    if testing_flag: dprint("NOW IN THE ELSE!!!  prod_syll = "+prod_syll,"blue")
                    syll_count +=1
                    target_onset,target_nuc,target_coda = get_syll_parts(target_syll) # getting onset/nucleus/coda parts of target syll
                    prod_onset,prod_nuc,prod_coda=get_syll_parts(prod_syll) # getting onset/nucleus/coda parts of produced syll

                    # if any of target_* or prod_* is '', then you've got a special case on your hands:
                    # if .........: ............
                    # special_case_error_type = "special case error type would go here"
                    if testing_flag: dprint(target_syll+" > " + prod_syll,"green")
                    if prod_onset != target_onset:  # if onsets do not match, there's an error
                        if testing_flag: dprint("[onsets don't match] About to investigate the following (i.e. going into compare_parts(): "+target_onset+" > "+prod_onset+" (set "+str(set_num),"blue")
                        onset_error_type=compare_parts("onset",target_onset,prod_onset,set_num,target_coda)  #target_coda in case it's a controlled set
                        dprint(">>>>> ok, got an onset_error here: "+onset_error_type,"blue")

                        # ok done determining stuff concerning the error(s) in the onsets of current target, produced syllable pair;
                        #   now add the error info to the list of errors
                        error = {} # reset
                        error["syll id"] = syll_id
                        error["error count"] = error_count; error_count+=1
                        #dprint ("\tincrementing error count to "+str(error_count),"blue")
                        error["target cluster"] = error["target onset"] = target_onset
                        error["prod cluster"] = error["produced onset"] = prod_onset
                        error["error type"] = onset_error_type
                        error["syll part"] = "onset"
                        error["syll"] = target_syll+" > " + prod_syll
                        error["syll count"] = syll_count
                        all_errors.append(error)


                    if prod_coda != target_coda: # codas do not match, there's an error
                        if testing_flag: dprint("\t[codas don't match] About to investigate the following (i.e. going into compare_parts(): "+target_coda+" > "+prod_coda+" (set "+str(set_num),"blue")
                        error = {} #reset
                        error["syll id"] = syll_id
                        error["error count"] = error_count; error_count+=1
                        #dprint ("\tincrementing error count to "+str(error_count),"blue")
                        error["target cluster"] = error["target coda"] = target_coda
                        error["prod cluster"] = error["produced coda"] = prod_coda
                        error["syll part"] = "coda"
                        error["syll"] = target_syll+" > " + prod_syll
                        error["syll count"] = syll_count

                        if prod_coda: # there WAS a coda produced
                            coda_error_type=compare_parts("coda",target_coda,prod_coda,set_num,target_onset)
                            error["error type"] = coda_error_type
                            dprint(">>>>> ok, got a coda_error here: "+coda_error_type,"blue")
                        else: # no coda was produced
                            error["error type"] = "coda cluster totally deleted"
                            dprint(">>>>> no coda even produced so error type = 'coda cluster totally deleted'","blue")

                        all_errors.append(error)

                    elif prod_onset==target_onset and prod_coda==target_coda:  # so syllables don't match some other way
                        if testing_flag: dprint("\t[syll no match some other way, so not going into compare_parts","blue")
                        dprint(">>>>> ok, got some other error type here: "+ some_other_error_type,"blue")
                        some_other_error_type = "some other kind of error type (neither coda nor onset mismatch)"

                error = {} #reset
                error["syll id"] = syll_id
                error["error count"] = error_count; error_count+=1# print(e["syll id"]+"; "+e["very broad error type"],"green")
                #dprint("some other kind of error....... here is stuff in error var: "+str(error),"green")
                #print("some other kind of error....... here is stuff in e: " +e)

                #error["error type"] = some_other_error_type
                error["error type"] = "some other kind of error type (neither coda nor onset mismatch)"
                error["syll part"] = "not coda or onset -- some other part mismatch"
                error["syll"] = target_syll+" > " + prod_syll
                error["syll count"] = syll_count
                error["target cluster"] = error["prod cluster"] = "n/a"
                all_errors.append(error)

        #
        #
        """  BELOW CHANGING ACTUAL e's SO THEN WHEN YOU PASS THE all_errors DICT TO writeCSV(), it'll get there in the format you want.
           So the changes are:
               1. to each error (dict), add {"broad error type":e["error type"]}
               2. to each error (dict), add {"very specific error type": << build, e.g. e["produced onset"]+ "_onset_"+e["error type"] >> }
        """
        for e in all_errors:	    # determine two features: "very broad error type" and "very specific error type"
            e["very broad error type"] = "****************************** DIDN'T FIND VERY BROAD ERROR TYPE" #default?
            if e["syll part"]=="onset": 	# ONSETS
               # print("looped, wtf============================================================")
                if e["error type"]=="WHOLE_CLUSTER_MV_LEGAL":
                    e["very specific error type"] =  e["produced onset"]+ "_onset_"+e["error type"]
                    e["very broad error type"] = e["error type"]
                elif e["error type"]=="WHOLE_CLUSTER_MV_ILLEGAL":
                    e["very specific error type"] =  e["produced onset"]+ "_onset_"+e["error type"]
                    e["very broad error type"] = e["error type"]
                elif e["error type"]=="CLUSTER_REPAIR-CONS_DELETION":
                    e["very specific error type"] =  e["target onset"]+ "_onset_"+e["error type"]
                    e["very broad error type"] = e["error type"]
                elif e["error type"]=="CLUSTER_REPAIR-VOWEL_EPENTHESIS":
                    e["very specific error type"] =  e["target onset"]+ "_onset_"+e["error type"]
                    e["very broad error type"] = e["error type"]
                else:
                    e["very specific error type"] = e["target onset"]+">"+e["produced onset"]+ "_onset_OTHER"
                    e["very broad error type"] = "OTHER"
            elif e["syll part"]=="coda":	# CODAS
                if e["error type"]=="WHOLE_CLUSTER_MV_LEGAL":
                    e["very specific error type"]=  e["produced coda"]+ "_coda_"+e["error type"]
                    e["very broad error type"] = e["error type"]
                    #e["very broad error type"] = e["WHOLE_CLUSTER_MV"]
                elif e["error type"]=="WHOLE_CLUSTER_MV_ILLEGAL":
                    e["very specific error type"]=  e["produced coda"]+ "_coda_"+e["error type"]
                    e["very broad error type"] = e["error type"]
                    #e["very broad error type"] = e["WHOLE_CLUSTER_MV"]
                elif e["error type"]=="CLUSTER_REPAIR-CONS_DELETION":
                    e["very specific error type"]=  e["target coda"]+ "_coda_"+e["error type"]
                    e["very broad error type"] = e["error type"]
                    #e["very broad error type"] = "CLUSTER REPAIR"
                elif e["error type"]=="CLUSTER_REPAIR-VOWEL_EPENTHESIS":
                    e["very specific error type"]=  e["target coda"]+ "_coda_"+e["error type"]
                    e["very broad error type"] = e["error type"]
                    #e["very broad error type"] = "CLUSTER REPAIR"
                else:  #  another error type, involving coda
                    e["very specific error type"] = e["target coda"]+">"+e["produced coda"]+ "_coda_OTHER"
                    e["very broad error type"] = "OTHER"
            elif e["error type"]=="OMIT":	# OMIT
                e["very specific error type"] =  e["very broad error type"]= e["error type"]

            else:  	# OTHER
        #if e["syll part"]=="n/a":  # so far this is for "?" and "OMIT" and something else, like "some other kind of error type (neither coda nor onset mismatch)"
                e["very specific error type"] = e["syll"]+"_"+e["error type"]
                e["very broad error type"] = "OTHER"

        #
        #
        writeCSV(subj_id,all_errors)        # write results to files
        write_results_and_diffs()	# outputting all the results and diffing (i.e. unit testing, sorta) and the results of the diffing..
#
#
#
#
if __name__ == "__main__":
    #dprint(__file__+" in "+__name__+". . . . ","blue")
    main()
    dprint("*****************************************************************************\n\
\t\tNOTE: only do FIRST 64 SETS for the 96ers!!!\n\t\t\t(right????)\n\
*****************************************************************************", "red")
    dprint("NOTE: nothing is happening multiple times, they're different seq, not just sets, remember...  but still why so many incorrect syllables. keep eye on syll count \n\
*****************************************************************************", "red")
#################################################################
#  python style conventions........
#   [http://www.python.org/dev/peps/pep-0008/]
# docstrings: http://www.python.org/dev/peps/pep-0257/
#
#  ALIGNMENT (& camelCasing vs underlines)
# Aligned with opening delimiter
#          foo = long_function_name(var_one, var_two,
#                                   var_three, var_four)
#
#          # More indentation included to distinguish this from the rest.
#          def long_function_name(
#                  var_one, var_two, var_three,
#                  var_four):
#              print(var_one)
#
#  CLASSES IN UPPER-CASE..  def's with underlines
# class Rectangle(Blob):
#
#        def __init__(self, width, height,
#                     color='black', emphasis=None, highlight=0):
#
#  DOCSTRINGS:
#   DEF's
#   def function(a, b):
#    """Do X and return a list."""
#
# def complex(real=0.0, imag=0.0):
#    """Form a complex number.
#
#    Keyword arguments:
#    real -- the real part (default 0.0)
#    imag -- the imaginary part (default 0.0)
#
#    """
#    if imag == 0.0 and real == 0.0: return complex_zero
#    ...
#################################################################


