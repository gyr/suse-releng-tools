local config = {
    common = {
        api_url = "https://api.suse.de/",
        default_project = "SUSE:SLFO:Main",
    },
    artifacts = {
        default_product = "SUSE:SLFO:Products:SLES:16.0",
        images_pattern = "\\b(kiwi-templates-Minimal|agama-installer-SLES)\\b",
        prodcuts_pattern = "\\b(000productcompose:)\\b",
    },
}

return config
