#!/usr/bin/env python

import optparse # deprecated; use argparse

#####  should be a simple bash script
# stitch together all the subj*_frequencies_table.csv's

############  colors for testing !!!!! #########################
class bcolors:
    MAGENTA = '\033[95m'; BLUE = '\033[94m'; GREEN = '\033[92m'; YELLOW =  '\033[93m'; RED = '\033[91m'; ENDC = '\033[0m'

    def disable(self):
        self.MAGENTA= self.BLUE = self.GREEN = self.RED = self.YELLOW = self.ENDC = ''

def dprint(print_str,color_str):
    """ print colored statements for debugging 
    
        print_str -- string to print
        color_str -- name of color, e.g. BLUE, GREEN, etc
    """
    if color_str == "blue": print bcolors.BLUE+print_str+bcolors.ENDC
    elif color_str == "red": print bcolors.RED+print_str+bcolors.ENDC     
    elif color_str == "magenta": print bcolors.MAGENTA+print_str+bcolors.ENDC     
    elif color_str == "green": print bcolors.GREEN+print_str+bcolors.ENDC     
    else: print color_str

def main():
   # all possible errors interested in right now
#    broad_error_types = ["WHOLE_CLUSTER_MV_LEGAL","WHOLE_CLUSTER_MV_ILLEGAL","CLUSTER_REPAIR-CONS_DELETION","CLUSTER_REPAIR-VOWEL_EPENTHESIS","OTHER"]
    broad_error_types=["Cluster","Move - legal","Move - illegal","C deletion","V epenthesis","Other"]
    all_cl = ["gv","tl","dr","sk","vd","lg","rk","st"]

    # initialize 
    all = {}
    for cl in all_cl: 
        all[cl]={} 
        for b in broad_error_types:  
            all[cl].update({b:0}) 


    #################  usage/help stuff  ####################################
    usage = "usage: %prog name_of_dir_with_files_to_add_up name_of_output.csv"
    parser = optparse.OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args) != 2: parser.error("specify 2 argument: the name of the dir holding frequency_table.cvs's to add up and the name of the output csv")

    csv_dir= args[0]
    outfile=args[1]

    #############################################################################
    # For each CSV file, create and save graph
    #############################################################################
    #for infile in glob.glob(os.path.join(csv_dir, '*.csv') ):
    for file in glob.glob(os.path.join(csv_dir, '*_frequencies_table.csv') ):
        #dprint("file: "+infile, "green"); dprint("... replacing header string ... ","blue")
        f = open(file)
        lines = f.readlines()
        for line in lines: 
            curr_cl = line.split(",")[0]
            #if line.split(",")[0] in all_cl:
            if curr_cl in all_cl:
                #all[line.split(",")[0]] += int(line.split(",")[1])
                dprint(curr_cl,"blue")
                dprint(line,"green")
                c = 1
                for b in broad_error_types:
                    where_look = broad_error_types.index(b)+1
                    print "looking at [",b, ",",line.split(",")[0],"); gonna add ",int(line.split(",")[c])
                    print "to...."
                    print all[line.split(",")[0]][b]
                   # all[line.split(",")[0]][b] += int(line.split(",")[where_look])
                    all[line.split(",")[0]][b] += int(line.split(",")[c])
                    c+=1
                print "so now it's ", all[line.split(",")[0]]
                print "\n"
        f.close()
    
    print(str(all))

    f = open(outfile,"w")
    f.write("CLUSTER,"+",".join(broad_error_types)+"\n")  # write headers
    for cl in all_cl:  
        s = cl
        for b in broad_error_types:
            s += ","+str(all[cl][b])
            print "just added ",b," (", str(all[cl][b]), " )supposedly; now s is ",s
        #print cl+","+",".join(str(i) for i in all[cl].values())
        #f.write(cl+","+",".join(str(i) for i in all[cl].values())+"\n")
        print s+"\n"
        f.write(s+"\n")
    f.close()


if __name__ == "__main__":
    main()
