local config = {
    common = {
        api_url = "https://api.suse.de/",
        default_project = "SUSE:SLFO:Main",
    },
    artifacts = {
        default_product = "SUSE:SLFO:Products:SLES:16.0",
        repositories = { "images", "product" },
        images_pattern = "\\b(kiwi-templates-Minimal)\\b",
        products_pattern = "\\b(000productcompose:)\\b",
        invalid_extensions = {
            ".json",
            ".milestone",
            ".packages",
            ".sha256",
            ".asc",
            ".report",
            ".rpm",
            ".verified",
        },
        invalid_start = "_",
        get_repo_info = function(self, index)
            local l_name
            local l_pattern
            if 1 == index then
                l_name = self.artifacts.repositories[1]
                l_pattern = self.artifacts.images_pattern
            elseif 2 == index then
                l_name = self.artifacts.repositories[2]
                l_pattern = self.artifacts.products_pattern
            end
            return {
                name = l_name,
                pattern = l_pattern,
                invalid_extensions = self.artifacts.invalid_extensions,
                invalid_start = { self.artifacts.invalid_start, l_name },
            }
        end
    },
}

return config
