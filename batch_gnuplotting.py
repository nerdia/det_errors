#!/usr/bin/env python

################################################################
#  take all csv's in a dir and send to gnuplot
#  pass dir with csv's
###############################################################
import os, glob
import Gnuplot  # ???????????
import optparse # deprecated; use argparse
import fileinput, sys # for replaceAll(....)

def main():
    #################  usage/help stuff  ####################################
    usage = "usage: %prog name_of_dir_with_CSVs"
    parser = optparse.OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args) != 1: parser.error("specify 1 argument: the name of the dir holding the CSV files")

    csv_dir= args[0]

    #############################################################################
    # For each CSV file, create and save graph
    #############################################################################
    #for infile in glob.glob(os.path.join(csv_dir, '*.csv') ):
    for infile in glob.glob(os.path.join(csv_dir, '*_frequencies_table.csv') ):
        dprint("file: "+infile, "green"); dprint("... replacing header string ... ","blue")
        # search for awkwardly-named header and renaming so the labels on the graphs don't suck...
        # Kind of an ad hoc solution to put this here; will have to change at some earlier time
        #replaceAll(infile,"CLUSTER,WHOLE_CLUSTER_MV_LEGAL,WHOLE_CLUSTER_MV_ILLEGAL,CLUSTER_REPAIR-CONS_DELETION,CLUSTER_REPAIR-VOWEL_EPENTHESIS,OTHER", "Cluster,Intact-cluster movement - legal,Intact-cluster movement - illegal,Cluster repair - consonant deletion,Cluster repair - vowel epenthesis,Other")
        replaceAll(infile,"CLUSTER,WHOLE_CLUSTER_MV_LEGAL,WHOLE_CLUSTER_MV_ILLEGAL,CLUSTER_REPAIR-CONS_DELETION,CLUSTER_REPAIR-VOWEL_EPENTHESIS,OTHER", "Cluster,Move - legal,Move - illegal,C deletion,V epenthesis,Other")
        g = Gnuplot.Gnuplot(debug=1) # create plot object
        g.reset()
        # graph title is the name of the CSV file, for now at least
        #just_file_name = os.path.splitext(os.path.basename(infile))[0]   #Returns the final component of a pathname; take off ext.
        just_file_name = os.path.basename(infile)   #Returns the final component of a pathname
        title = just_file_name; dprint ("title will be :"+title, "green")
        g.title(title)

        # graph will be a .png with same name as filename (incl ".csv"),
        #   except with type of graph and ".png" added
#        png_filename = infile+"_histogram.png"
#        g("set terminal png") # save file as png
#        g("set output '"+png_filename+"'"); dprint ("graph going into: "+png_filename, "green")

        ps_filename = os.path.splitext(infile)[0]+"_histogram.ps"
        dprint("file: "+infile, "green"); 
        g("set terminal postscript solid color font 'Verdana' 12 size 9,6") # save file as ps
        #g("set terminal png nocrop enhanced font Vera 9 size 600,550")
        g("set output '"+ps_filename+"'"); dprint ("graph going into: "+ps_filename, "green")


        #############################################################################
        # set type of histogram chart (clustered/stacked/clustered+errorbars)
        #   and various other style attributes
        #############################################################################
        g("set style data histogram")
        g("set style histogram rowstacked title  offset character 0, 0, 0 ")

        # ERROR BARS:
        # note that for errorbars mode, you can't do stacked by definition!
        # The errorbars style is very similar to the clustered style, except that it requires two
        # columns of input for each entry. The first column is treated as the height (y-value) of that
        # box, exactly as for the clustered style. The second column is treated as an error magnitude,
        # and used to generate a vertical error bar at the top of the box. The appearance of the error
        # bar is controlled by the current value of set bars and by the optional 5#5linewidth6#6
        # specification.
        #set style histogram errorbars {gap <gapsize>} {<linewidth>}

        # what the bars look like
        g("set boxwidth 0.6 absolute")
        #g("set style fill solid border -1")  # fill with color
        #g("set style fill pattern 2 border -1") # fill with pattern -- nice for color graphs
        g("set style fill pattern 3 border -1") # better fill pattern for printing in black and white
        #g("set style gap 2")

        g("set border 0")

        # LABEL STUFF: 
        """FROM PACO::::::::::::::::::::::::::::::::::
        Yep.  To use the dual-axis you need to call the command "set axisy1y2" or something like that.  I don't have my code in front of me right now, but I think google should make it easy to find (or ask tomorrow when I'm at the office).  The xlabel stuff I'm sure is possible, but not something I've ever used myself.  This is the website I go to for many of my gnuplot questions: http://t16web.lanl.gov/Kawano/gnuplot/plot3-e.html#5.10.  I assume you use the numpy and math libraries?  Other than that, I don't use anything special.  I guess one could use commands like 'sum' or whatever, but honestly, I just use a for loop since it feels more transparent to me, tho it gives the same result either way.  If you want to come by office tomorrow afternoon I could help you with your code."""
        g.xlabel("Clusters"); g.ylabel("Number of errors") # g.ylabel("Error rate (vs all? vs blah)")
        g("set grid noxtics nomxtics ytics nomytics noztics nomztics nox2tics nomx2tics noy2tics nomy2tics nocbtics nomcbtics")
        g("set xtics nomirror; set ytics nomirror")
        #g("set grid layerdefault   linetype 0 linewidth 1.000,  linetype 0 linewidth 1.000")
        g("set yrange [ 0.00000 : * ] noreverse nowriteback")
        #set xtics border in scale 1,0.5 nomirror rotate by -45  offset character 0, 0, 0
        # set label (=key) options
        g("unset key")
        g("set key width -4 nobox")
        #g("set key outside right center vertical Left reverse enhanced autotitles columnhead")
        g("set key outside right center vertical Left reverse autotitles columnhead")
        g("set key samplen 3 spacing 4")
        #g("set key box linetype -1 linewidth 1.000; ")
        #g("set style histogram rowstacked title  offset character 0, 0, 0 ")
       # g("set yrange [ 0 : 100 ] noreverse nowriteback")
        #g("set terminal png nocrop enhanced font Vera 9 size 600,550")
        
        g("set datafile separator ','")    # set delimiter/separator to be " "
        g("set datafile missing('-')") # missing data represented by "-" in the data file
        
        g.plot("'"+just_file_name+"' using 3:xtic(1) ti col, '' u 2 ti col, '' u 4 ti col, '' u 5 ti col ")  # xtic(1) means label on things in the first column")
        #g.replot()
        #g("show key")


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


def replaceAll(file,searchExp,replaceExp):
    """ search and replace strings in a file
            ex usage: replaceAll("/fooBar.txt","Hello\sWorld!$","Goodbye\sWorld.")  """
    dprint("here in replaceAll","red")
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp,replaceExp)
        sys.stdout.write(line)



if __name__ == "__main__":
    main()
