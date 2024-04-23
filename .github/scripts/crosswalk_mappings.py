#provides a mapping between keys in the ro-crate dictionary (left)
#and keys in issue dictionary (which are the values in the mapping)
#None value indicate default values or properties which we not attempt to automatically fill
#they should nothing apart from map between

root_node_mapping = {"@id":"./",
            "identifier": None,
            "@type":None,
            "alternateName":"slug",
            "name":"title",
            #abstract used to provide a description of the model
            "abstract":"abstract",
            #description used for higher level overview of M@TE and metadata
            #this gets filled in from the Project Description text from https://github.com/ModelAtlasofTheEarth/metadata_schema/README.md
            "description":None,
            "creator":"creators",
            #"contributor":"contributor",
            "citation":"publication",
            "publisher":None,
            "license":"license",
            "keywords":"scientific_keywords",
            "about":"for_codes",
            "funder":"funder",
            "funding":"funding",
            "version":None,
            "temporalCoverage":None,
            "Spatial extents":None,
            "spatialCoverage":None,
            "isBasedOn":None,
            "isPartOf":None,
            "creativeWorkStatus":"model_status"
            }


model_inputs_node_mapping = {"@id":"model_inputs",
            "identifier": ["model_code_inputs.doi"],
            "@type":None,
            "description":None,
            "creator":"creators",
            "author":None,
            "version":None,
            "programmingLanguage":None,
            "keywords":None,
            "runtimePlatform":None,
            "memoryRequirements":None,
            "processorRequirements":None,
            "storageRequirements":None}


model_outputs_node_mapping = {"@id":"model_outputs",
            #the list around certain items in the mapping cause the same structure to appear in teh RO-Crate
            "identifier": ["model_output_data.doi"],
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
            "fileFormat":None
            }


dataset_creation_node_mapping = {"@id":"#datasetCreation",
            "@type":None,
            "agent":"model_output_data.creators",
            "description":None,
            "startTime":None,
            "endTime":None,
            "instrument":["software", "computer_resource"],
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
    'for_codes':'for_codes.termCode',
    'status':'foo',
    'doi':'foo',
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
    #"contributors.name":"contributors.givenName",
    #"contributors.family_name":"contributors.familyName",
    #"contributors.ORCID":"contributors.@id",
    'creators.name': 'creators.givenName',
    'creators.family_name': 'creators.familyName',
    'creators.ORCID': 'creators.@id',
    "associated_publication.authors":"publication.author",
    "associated_publication.title":"publication.name",
    "associated_publication.doi":"publication.@id",
    "associated_publication.url":"publication.url",
    #currently the mapping functionality cannot handle the heavilty nested
    #structure of publications, requiring access like issue_dict['publication']['isPartOf'][0]['isPartOf']['name'][0]
    #so these get added as a hack in the function configure_yaml_output_dict
    "associated_publication.journal":"foo",
    "associated_publication.publisher":"foo",
    #Not sure how robust this compute section will be, as it's designed around the DOI record for Gadi
    #but would be good to extend so do something get RORs and URLs
    "compute_info.name":"computer_resource.name",
    "compute_info.organisation":"computer_resource.author.name",
    "compute_info.url":"computer_resource.url",
    "compute_info.doi":"computer_resource.@id",
    "research_tags":"scientific_keywords",
    "compute_tags":"software.keywords",
    "funder.name":"funder.name",
    "funder.doi":"funder.@id",
    "funding.name":"funding.funder.name",
    "funding.doi":"funding.funder.@id",
    "funding.number_id":"funding.identifier",
    #"funding.url":"foo", #this can/should be added without breaking the website
    "abstract":"abstract",
    "images.landing_image.src":"landing_image.filename",
    "images.landing_image.caption":"landing_image.caption",
    "images.graphic_abstract.src":"graphic_abstract.filename",
    "images.graphic_abstract.caption":"graphic_abstract.filename",
    "images.model_setup.src":"model_setup_figure.filename",
    "images.model_setup.caption":"model_setup_figure.caption",
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
