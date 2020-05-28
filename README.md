
**T**ransit and **R**adial velocity **I**nteractive **F**itting tool for **O**rbital analysis and **N**-body simulations: **The Exo-Striker** 

<p align="center">
  <img width="400" src="https://github.com/3fon3fonov/trifon/blob/master/lib/UI/33_striker.png">
</p>
 
The Exo-Striker analyzes exoplanet orbitals, performs N-body simulations, and models the RV stellar reflex motion caused by dynamically interacting planets in multi-planetary systems. It offers a broad range of tools for detailed analysis of transit and Doppler data, including power spectrum analysis for Doppler and transit data; Keplerian and dynamical modeling of multi-planet systems; MCMC and nested sampling; Gaussian Processes modeling; and a long-term stability check of multi-planet systems. The Exo-Striker can also perform Mean Motion Resonance (MMR) analysis, create fast fully interactive plots, and export ready-to-use LaTeX tables with best-fit parameters, errors, and statistics. It combines Fortran efficiency and Python flexibility and is cross-platform compatible (MAC OS, Linux, Windows). 

![new_es](https://github.com/3fon3fonov/trifon/blob/master/lib/png/Exo_striker_demo_image.png)
 
**Developer**

* Trifon Trifonov, MPIA Heidelberg.

* with contributions by Mathias Zechmeister, Jakub Morawski, Man Hoi Lee, Stefan Dreizler and Grigorii Smirnov-Pinchukov


**What works**:

* RV signal and alias search: via GLS periodogram & maximum lnL periodogram (MLP).
* Activity index signal search via GLS periodogram.
* Keplerian and Dynamical modeling of RV & Transit photometry exoplanet data.
* Instant online access to the "RVBank" database (over 212 000 RVs and activity indices of about HARPS 3000 stars & over 64 000 RVs and activity indices of about HIRES 1700 stats !!!).
* Transit signal search (via "TLS").
* Interactive transit photometry detrending (via "wotan"), and interactive outlier removal.
* GP modeling (only SHO and Rot. GP "celerite" kernels integrated so far).
* Joint RVs + Transit + GPs best-fit optimization.
* Joint RVs + Transit + GPs MCMC/Nested Sampling (via "emcee" & "dynesty").
* TTVs and/or joint TTVs + RVs analysis.
* RV auto-fit (RV automated planet-finder algorithm).
* Fit for apsidal orbital precession, or apply General Relativity (GR) precession. 
* Instant AMD stability check for multiple planetary systems (including during optimization or MCMC/Nested Sampling).
* Long-term stability check of multiple planetary systems using SyMBA, MVS, and MVS with a GR precession.
* Various of minimization methods (via "SciPyOp").
* Fully interactive, super-fast, high-quality, exportable plots.
* RV vs. Activity time-series correlation analysis/plots.
* Import/Export of work sessions and multi-sessions. 
* Export plots to a matplotlib window for further customization.
* Export ready to use LaTeX tables with best-fit parameters, errors, and statistics. 
* Handy text-editor and calculator tools.
* Multi-platform: It works on MAC OS (10.6+), Linux (Suse, Mint, Ubuntu, etc.) and Windows 10.
* Integrated Bash-shell (Linux only).
* Integrated Jupyter shell.
* Importable as a standard python library (i.e., ideal for scripting and notebooks, see "Notebook_and_script_examples").
* Print the GUI screen into a .jpeg/.png image (useful for sharing quick results, just like the image above).

**What is to be implemented**:

* More GP kernels (work in progress). 
* Larger arsenal of N-body/dynamical simulation/analysis tools (+ REBOUND is planned to be included). 
* Internal TTV and photo-dynamical modeling (i.e. the external "TTVFast" will become a secondary option).
* Combined modeling with Astrometry.
* Documentation, Instructions, and Video tutorials (work in progress here: https://exostriker.readthedocs.io)



**Installation:**


Currently there are three ways to install/run The Exo-Striker:    

#######################################################    
*  The simpliest way to "git clone"    

$ git clone https://github.com/3fon3fonov/exostriker  

and then:    

$ cd exostriker  
$ python exostriker_gui.py    

Generally, you do not need to install anything if you already have all the dependencies needed for the tool to run. For the dependency list, see the "setup.py" file.    
The Exo-Striker will automatically compile the Fortran code for you at the first start of the program and will keep you updated if the source code was updated (if you regularly "git pull").    
 
 
#######################################################    
*  The second way to instal the tool is:    

$ git clone https://github.com/3fon3fonov/exostriker     

and then:    

$ cd exostriker    
$ python setup.py install    

This will (hopefully) install the tool in your system.     
Then, open a terminal and     

$ exostriker    

Should start the Exo-Striker  


#######################################################    
*  and last, you can try:    

$ pip install git+https://github.com/3fon3fonov/exostriker    

This will (hopefully) install the tool in your system.    
Then, open a terminal and     

$ exostriker

Should start the Exo-Striker  

#######################################################     

If you still cannot boot the tool after a 'successful' installation, please try:

$ python exostriker_gui.py -debug 

or 

$ exostriker -debug 

(depending on how you use the tool)

Then, copy the output error, and please open a 'GitHub' issue. Otherwise, all possible problems/bugs/crashes will be displayed on the 
'stdout/stderr' tab of the tool. If you use this tool, and you find a bug or a problem, please report it!    

#######################################################

Please keep in mind that this software is developed mostly for my needs and for fun. I hope, however, that you may find it capable of solving your scientific problems, too.

Feedback and help in further development will be highly appreciated!
A wish-list with your favorite tools and methods to be implemented is also welcome!    

Just open an "Issue" on the GitHub, or send a PM to trifonov@mpia.de.    
Few comments to understand your new setup better.



**Credit**

If you made the use of The Exo-Striker for your paper, I would appreciate if you give credit to it.
As it is unlikely that I will find time to write a refereed paper on The Exo-Striker soon, please cite the tool with its ASCL ID ascl:1906.004 (see https://ascl.net/1906.004).    
 
The Exo-Striker relies on many open-source packages, which if you had made the use of (some of) them while working with the tool, 
you should acknowledge too. (It is your responsibility to find the correct references in the literature):    


* The interactive plotting is done with a custom version of the "pyqtgraph": 

http://www.pyqtgraph.org/

* "GLS" and "MLP" periodograms are taken from Mathias Zechmeister's repo: 

https://github.com/mzechmeister/python

* "TLS" and "wotan" are taken from: 

https://github.com/hippke/tls

https://github.com/hippke/wotan

* The transit modeling is done with "batman":
 
https://github.com/lkreidberg/batman

* MCMC sampling is done with "emcee": 

https://github.com/dfm/emcee

* Nested Sampling is done with "dynesty": 

https://github.com/joshspeagle/dynesty

* TTV models are adopted from "TTVfast-python":

https://github.com/mindriot101/ttvfast-python

* The "Text editor" used in the tool is a hack between "Megasolid Idiom" 
and "PyEdit2":

https://github.com/mfitzp/15-minute-apps/tree/master/wordprocessor

https://github.com/Axel-Erfurt/PyEdit2

* N-body tests are performed using a custom version of the "Swift" N-body library,
modified by Man Hoi Lee (HKU) and Trifon Trifonov (MPIA).

https://www.boulder.swri.edu/~hal/swift.html

* Additionally, the Exo-Striker uses many "standard" Python libraries like 
"PyQt5", "matplotlib", "numpy", "scipy", "dill", "Jupyter", "qtconsole",
and more.


**Scientific papers which used The Exo-Striker (to my knowledge):**

* Stock, S., J. Kemmer, S. Reffert, et al. (2020). The CARMENES search for exoplanets around M dwarfs. Characterization of the nearby ultra-compact multiplanetary system YZ Ceti. (A&A, in press) arXiv e-prints arXiv:2002.01772.
 
* Trifonov, T., M. H. Lee, M. Kürster, et al. (2020). The CARMENES search for exoplanets around M dwarfs. Dynamical characterization of the multiple planet system GJ 1148 and prospects of habitable exomoons around GJ 1148 b. (A&A, in press) arXiv e-prints arXiv:2002.00906.

* Trifon Trifonov, Lev Tal-Or, Mathias Zechmeister, et al. (2020). A public HARPS radial velocity database corrected for systematic errors. A&A, 636, A74 
 
* Luque, R., T. Trifonov, S. Reffert, et al. (2019). Precise radial velocities of giant stars. XIII. A second Jupiter orbiting in 4:3 resonance in the 7 CMa system. ApJ, 631, A136.

* Trifonov, Trifon, Stephan Stock, Thomas Henning, et al. (2019). Two Jovian Planets around the Giant Star HD 202696: A Growing Population of Packed Massive Planetary Pairs around Massive Stars?. AJ, 157, 93.

* Trifonov, Trifon, Jan Rybizki, and Martin Kürster. (2019). TESS exoplanet candidates validated with HARPS archival data. A massive Neptune around GJ 143 and two Neptunes around HD 23472. A&A, 622, L7. 

(And as of April 2020, I am aware of at least 7 more papers in preperation !!!)


