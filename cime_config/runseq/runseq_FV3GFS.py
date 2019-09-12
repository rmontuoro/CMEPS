#!/usr/bin/env python

import os, shutil, sys

_CIMEROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..","..","..","..")
sys.path.append(os.path.join(_CIMEROOT, "scripts", "Tools"))

from standard_script_setup import *

logger = logging.getLogger(__name__)

def runseq(case, coupling_times):

    rundir    = case.get_value("RUNDIR")
    caseroot  = case.get_value("CASEROOT")

    atm_cpl_dt = coupling_times["atm_cpl_dt"]

    outfile   = open(os.path.join(caseroot, "CaseDocs", "nuopc.runseq"), "w")

    logger.info("NUOPC run sequence: with cpl time step")
    outfile.write ("runSeq::                                \n")
    #outfile.write ("@" + str(atm_cpl_dt) + "                \n")
    outfile.write ("   ATM                                  \n")
    #outfile.write ("@                                       \n")
    outfile.write ("::                                      \n")

    outfile.close()
    shutil.copy(os.path.join(caseroot, "CaseDocs", "nuopc.runseq"), rundir)
