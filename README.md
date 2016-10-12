Propagation Database
======

(c) 2015 - 2016


Setup
-----

1. Get the repository  
  ```bash 
  $ git clone https://github.com/gnwong/propdb.git
  ```  

2. Attempt to run the `setup.py` program in `propdb/tools/`  
  ```bash 
  $ sudo python setup.py   
  ```  
  Follow the instructions of the setup script (installing packages as necessary).  

3. Move any database packages into the `propdb/` directory.  

4. From the propdb/tools directory, run the following script to unpack the/each data package  
  ```bash  
  $ python unload-package.py <MeasurementCampaign.tar>  
  ```  
  being sure to use the package name instead of `<MeasurementCampaign.tar>` and including the `.tar` extension.  

5. Again, for each data package, run the following script to load the dataset into the
  database
  ```bash
  $ python loader.py <MeasurementCampaign>
  ```
  This time, note that the `.tar` extension should not be included.

Use (Starting the server)
-----

1. Open up a terminal and navigate to the package/public folder. 
2. Run the following script to start the server
  ```bash
  $ python server.py
  ```

3. Access the database by going to [localhost:8080](localhost:8080) in your web browser.

Use (Data query)
-----

Users can cycle through available campaigns by clicking the [ Cycle Campaign (·) ] button at the left of the navigation bar. A different set of statistics has been computed for each campaign. Each of the available statistics can be used to search through the full dataset.

The set of boxes at the left side of the screen provides a means to do this — selecting any combination of query values and clicking the [ Filter ] button on the nav bar narrows down the presented dataset to only those raw measurements which correspond to the filter.

The set of all "valid" measurement populates the list at the right side of the screen. Clicking on any of the names in this list will bring up an image corresponding to the processed Power Delay Profile (PDP) for the selected raw measurement. If no processed image exists, a message "We apologize, but the requested image cannot be loaded." is displayed instead.

Any single query to the dataset is guaranteed to yield a nonempty subset of the data; however, multiple queries at the same time do not provide the same guarantee.

Use (Download)
-----

After identifying the files you desire, you can download the subset by clicking the [ Download Queries Files ] button. This will bring you to a new page containing information about your request and the location of a newly-created zip file containing the requested files.


