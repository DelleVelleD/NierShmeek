#!/usr/local/bin/python3

import sys

from dat_utils import *

def main():
	if len(sys.argv) < 2:
		print("need input directory")
		sys.exit(1)
	
	indir = sys.argv[1]
	outfile = indir.lstrip(".")
	if len(sys.argv) == 3:
		if indir[-3:] == "dat":
			outfile = "D:\\SteamLibrary\\steamapps\\common\\NieRAutomata\\data\\pl\\pl000d.dat"
		if indir[-3:] == "dtt":
			outfile = "D:\\SteamLibrary\\steamapps\\common\\NieRAutomata\\data\\pl\\pl000d.dtt"
	
	pack = FilePackInfo(indir)
	write = Writer(pack)
	write.setOutFile(outfile)
	write.write()


if __name__ == '__main__':
	main()