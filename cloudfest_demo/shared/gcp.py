import yaml
from google.cloud import secretmanager

class Secret:
    @staticmethod
    def access_secret_version(project_id, secret_id):
        """
        Access the payload for the given secret version if one exists. The version
        can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
        """

        # Create the Secret Manager client.
        client = secretmanager.SecretManagerServiceClient()

        # Build the resource name of the secret.
        name = client.secret_path(project_id, secret_id)

        # Get the secret.
        response = client.list_secret_versions(parent=name)
        latestVersion = ""
        latestVersionId = 0
        for secretVersion in response:
            myVersion = int(secretVersion.name.split('/')[-1])
            if myVersion > latestVersionId:
                latestVersionId = myVersion
                latestVersion = secretVersion.name

        # Access the secret version.
        response = client.access_secret_version(name=latestVersion)
        payload = response.payload.data.decode("UTF-8")
        return yaml.load(payload, Loader=yaml.FullLoader)