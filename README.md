# Welcome to the Model Atlas of The Earth (M@TE)

## Model submission overview and objectives

* M@TE models begin their life as github repositories, based on a [simple template](https://github.com/ModelAtlasofTheEarth/mate_model_template)
* New models are spawned using the [github issues functionality](https://github.com/ModelAtlasofTheEarth/Model_Submission/issues), within this repostory
* We provide workflows (using github actions) that aim to harvest and reuse as much existing metadata as possible, using persistent identifiers such as ORCiDs and RoRs
* The result is a model repository that comes with a rich metadata document, based on the [Ro-Crate](https://www.researchobject.org/ro-crate/) project
* This process also assembles material so we can feature you model on the [M@TE website](https://mate.science)

## What happens and when

*  M@TE models begin their life as Github repositories
*  To manage large file payloads, and to provide long term storage,  we copy your model repository to our server on NCI
*  This process also results in a DOI being minted for your model

## Model submission workflow:

_Note: Workflows are currently in development!_

**Make a new model request:** 
* open a new issue using the [New model request](https://github.com/ModelAtlasofTheEarth/Model_Submission/issues/new/choose)
* fill in as much information as you can and submit the issue
* This will trigger workflows that source metadata relavant to your model
* At the bottom will see a report on the information for

**Request a review:**
* If you are satisfied with the information contained in the report, 
* add a https://github.com/ModelAtlasofTheEarth/Model_Submission/labels/review%20requested label to the issue

**Model repository creation**
* The [model_reviewers](https://github.com/orgs/ModelAtlasofTheEarth/teams/model_reviewers) team will add an https://github.com/ModelAtlasofTheEarth/Model_Submission/labels/approved label to the issue
* this triggers the creation of a repository for your model based in this template

**Upload model to our [NCI](https://nci.org.au/) Server**
* Add an https://github.com/ModelAtlasofTheEarth/Model_Submission/labels/upload%20to%20NCI label to the model submission issue
* This will allow large file payloads (up to several 100s Gb) to be added to you model
* The [model_reviewers](https://github.com/orgs/ModelAtlasofTheEarth/teams/model_reviewers) team will contact you via email to orchestrate this process


**Model published**
* Your model will be https://github.com/ModelAtlasofTheEarth/Model_Submission/labels/published on the NCIs GeoNetworkCatalog
* It will recieve a DOI and this will be automatically added to your model metadata
* Your model will be featured on the M@TE website

# To do

- [ ] Fix file size limits, Add note like, larger files can be added to your model repository later
- [ ] Is the licence URL being handled properly? Check URL, (Add a set of images to the website, and associate each licence with an image)
- [x] Is there a visual cue for test running again - One option is to have the bot write a on-line "building model information"
- [ ] Need to add model contributor as an owner of the repository
- [ ] Check this text on this issue template: "Please check our [model repository](https://airtable.com/shrUcrUnd7jB9ChZV) to explore valid licenses."
- [ ] UX - explain between model code and software framework
- [ ] Can tick yes and no for "intending to submit data"
- [ ] If parse issue crashes, a developer/ bug label need to be added.
- [ ] Fix the call to Zenodo being hardcoded into the doi/Api
- [ ] Fix @id assigment if not found
- [ ] Edit permissions for issues?
