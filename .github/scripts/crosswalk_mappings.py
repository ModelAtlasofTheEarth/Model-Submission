#provides a mapping between keys in metadata (left)
#and keys in issue dictionary (which are the values in the mapping)
#None value indicate default values or properties which we not attempt to automatically fill
#this needs to refactored so that it looks for the approapriate @id

root_node_mapping = {"@id":"./",
            "@type":None,
            "name":"slug",
            "description":"description",
            "creator":"creators",
            "contributors":"contributor",
            "citation":"publication",
            "publisher":None,
            "license":"license",
            "keywords":"scientific_keywords",
            "about":"for_codes",
            "funder":"funder",
            "Dataset version":None,
            "Temporal extents":None,
            "Spatial extents":None,
            "Dataset lineage information":None,
            "Dataset format":None,
            "Dataset status":None,
            "hasPart":None
            }


model_inputs_node_mapping = {"@id":"model_inputs",
            "@type":None,
            "description":None,
            "creator":"creators",
            "author":None,
            "version":None,
            "programmingLanguage":None,
            "owl:sameAs":"model_code_uri",
            "keywords":None,
            "runtimePlatform":None,
            "memoryRequirements":None,
            "processorRequirements":None,
            "storageRequirements":None}


model_outputs_node_mapping = {"@id":"model_outputs",
            "@type":None,
            "description":None,
            "creator":"model_output_data.creators",
            "author":None,
            "version":None,
            "programmingLanguage":None,
            "fileFormat":None,
            }

website_material_node_mapping = {"@id":"website_material",
            "@type":None,
            "description":None,
            "creator":"creators",
            "author":None,
            "fileFormat":None
            }


dataset_creation_node_mapping = {"@id":"#datasetCreation",
            "@type":None,
            "agent":"model_output_data.creators",
            "description":None,
            "endTime":None,
            "endTime":None,
            "instrument":["software", "computer_uri"],
            "object":None,
            "result":None}

default_issue_entity_mapping_list = [root_node_mapping,
                model_inputs_node_mapping,
                model_outputs_node_mapping,
                website_material_node_mapping,
                dataset_creation_node_mapping]


#a limitation of the mapping is that where lists are present as values, the key needs to be the same on the both sides.
issue_yaml_mapping = {
    'templateKey':'foo',
    'slug': 'slug',
    'title': 'title',
    'date':'foo',
    'featuredpost':'foo',
    'for_codes':'for_codes.@id',
    'status':'foo',
    "software.name":"software.name",
    "software.doi":"software.@id",
    "software.url_source":"software.codeRepository",
    "licence.licence_url":"license.@id",
    "licence.licence_image":"license.website_path",
    "licence.description":"license.description",
    "licence.licence_file":"foo",
    "submitter.name":"submitter.givenName",
    "submitter.family_name":"submitter.familyName",
    "submitter.ORCID":"submitter.@id",
    "contributors.name":"contributors.givenName",
    "contributors.family_name":"contributors.familyName",
    "contributors.ORCID":"contributors.@id",
    'creators.name': 'creators.givenName',
    'creators.family_name': 'creators.familyName',
    'creators.ORCID': 'creators.@id',
    "associated_publication.title":"publication.name",
    #currently this generalised functionality cannot handle the heavilty nested
    #structure of publications
    #issue_dict['publication']['isPartOf'][0]['isPartOf']['name'][0]
    "associated_publication.journal":"foo",
    "associated_publication.publisher":"publisher",
    "associated_publication.doi":"publication.@id",
    "associated_publication.url":"publication.url",
    #The model submission workflow and web yaml have diverged a lot for the "compute section"
    "compute_info.name":"foo",
    "compute_info.organisation":"foo",
    "compute_info.computer_url":"computer_uri",
    "compute_info.computer_doi":"foo",
    "research_tags":"keywords",
    "compute_tags":"software.keywords",
    "funder.funder_name":"funder.name",
    "grants_funder.doi":"foo",
    "grants_funder.number_id":"foo",
    "grants_funder.url":"foo", #this can/shoudl be added without breaking the website
    "abstract":"description",
    "images.landing_image.src":"landing_image.filename",
    "images.landing_image.caption":"landing_image.caption",
    "images.graphic_abstract.src":"graphic_abstract.filename",
    "images.graphic_abstract.caption":"graphic_abstract.filename",
    "images.model_setup.src":"model_setup.filename",
    "images.model_setup.caption":"model_setup.caption",
    "animation.src":"animation.filename",
    "animation.caption":"animation.caption",
    #these may need rejigging,
    #the urls here will point to existing DOIs/URLS
    #but for the website they should point to the NCI collection
    'model_setup_info.url':'foo',
    'model_setup_info.summary':'model_setup_description',
    'model_files.url':'foo',
    'model_files.notes':'foo',
    'model_files.file_tree':'foo',
    "dataset.url":"model_data.url",
    "dataset.notes":"model_data.notes",
    "dataset.doi":"model_data.doi",
    "dataset.notes":"model_data.notes"
}
