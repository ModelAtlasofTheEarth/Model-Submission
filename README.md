# Welcome to the Model Atlas of The Earth (M@TE)

## Model submission overview and objectives

* M@TE models begin their life as github repositories, based on a [this repository template](https://github.com/ModelAtlasofTheEarth/mate_model_template)
* New models are spawned using the [github issues functionality](https://github.com/ModelAtlasofTheEarth/Model_Submission/issues), within this repository
* We provide workflows (using github actions) that aim to harvest and reuse as much existing metadata as possible, using persistent identifiers such as ORCiDs and RoRs
* The result is a model repository that comes with a rich metadata document, based on the [RO-Crate](https://www.researchobject.org/ro-crate/) project
* This process also assembles material so we can feature the model on the [M@TE website](https://mate.science)


## Model submission workflow:

**1) Make a new model request:**
* open a new issue using the [New model request](https://github.com/ModelAtlasofTheEarth/Model_Submission/issues/new/choose)
* fill in as much information as you can and submit the issue
* a https://github.com/ModelAtlasofTheEarth/Model_Submission/labels/new%20model label will appear on the original issue. 
* This will trigger workflows that collect this information and source additional metadata relavant to your model
* You will see a summary report for your model, including potential missing information or errors (e.g. URLs that didn't resolve)
  

**2) Editing and review:**

* By editing the first comment in the issue discussion, you will trigger a rebuild of the model information
* When you are satisfied with the information contained in the report, add a https://github.com/ModelAtlasofTheEarth/Model_Submission/labels/review%20requested label to the issue

**3) Model repository creation**
* The [model_reviewers](https://github.com/orgs/ModelAtlasofTheEarth/teams/model_reviewers) team will add an https://github.com/ModelAtlasofTheEarth/Model_Submission/labels/model%20approved label to the issue
* this triggers the creation of a mode under the M@TE organiazation, based on [this simple template](https://github.com/ModelAtlasofTheEarth/mate_model_template)
* the model metadata is stored as an [RO-Crate](https://www.researchobject.org/ro-crate/) (named `ro-crate-metadata.json`) in the top level of the repository. 
* A (https://github.com/ModelAtlasofTheEarth/Model_Submission/labels/model%20created) label will appear on your issue.
* The github account holder who submitted the model will have owner privillages.


**4) Clone and configure your model repository**

* Your model repository is now yours to customize and fill with files (payload)
* We encourage you to use github to add any material that is within github's typical repository limits (files < 100 Mb, total repository size < 5 Gb)
* You may customize the model repository as you feel fit. This may require editing of the metadata file () to reflect changes in directory structure.
* Push any changes back to the [M@TE organization](https://github.com/ModelAtlasofTheEarth/).  

**5) Upload model to our [NCI](https://nci.org.au/) Server**
* Add an https://github.com/ModelAtlasofTheEarth/Model_Submission/labels/upload%20to%20NCI label to the model submission issue
* Let us know (via the original issue) if you need to add additional files that exceed Github's limits
  * The [model_reviewers](https://github.com/orgs/ModelAtlasofTheEarth/teams/model_reviewers) team will contact you via email to orchestrate this process

**6) Model published**
* Your model will be published on the NCI [GeoNetworkCatalog](https://geonetwork.nci.org.au/geonetwork/srv/eng/catalog.search#/home)
* It will recieve a DOI and this will be automatically added to your model metadata
* Your model will be featured on the M@TE website
* a https://github.com/ModelAtlasofTheEarth/Model_Submission/labels/model%20published label will appear on the original issue. 

