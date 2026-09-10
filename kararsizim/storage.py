from whitenoise.storage import CompressedManifestStaticFilesStorage

class ForgivingCompressedManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """
    WhiteNoise storage that:
    1. Normalizes Windows backslashes (\\) to forward slashes (/) in stored names.
    2. Has manifest_strict = False so missing or un-hashed static files never raise ValueError / 500 errors.
    3. Gracefully falls back to the original unhashed file path.
    """
    manifest_strict = False

    def clean_name(self, name):
        return name.replace('\\', '/')

    def hashed_name(self, name, content=None, filename=None):
        try:
            result = super().hashed_name(name, content, filename)
            return result.replace('\\', '/')
        except (ValueError, Exception):
            return name.replace('\\', '/')

    def stored_name(self, name):
        try:
            # Look up with both forward and backward slashes to match Windows-generated manifests
            clean = name.replace('\\', '/')
            if clean in self.hashed_files:
                return self.hashed_files[clean].replace('\\', '/')
            
            # Try original name
            result = super().stored_name(name)
            return result.replace('\\', '/')
        except (ValueError, Exception):
            return name.replace('\\', '/')
