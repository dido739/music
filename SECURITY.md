# Security Updates

## December 2024 - yt-dlp Security Patch

### Vulnerabilities Addressed

**CVE: yt-dlp File system modification and RCE**
- **Severity**: High
- **Affected versions**: yt-dlp < 2024.07.01
- **Description**: File system modification and remote code execution through improper file-extension sanitization
- **Resolution**: Updated to yt-dlp >= 2024.07.01

**CVE: yt-dlp Command Injection (Bypass of CVE-2023-40581)**
- **Severity**: High  
- **Affected versions**: yt-dlp >= 2021.04.11, < 2024.04.09
- **Description**: Command injection when using `%q` in yt-dlp on Windows
- **Resolution**: Updated to yt-dlp >= 2024.07.01

### Changes Made

**requirements.txt:**
- ⬆️ Updated `yt-dlp` from `2023.12.30` to `>=2024.07.01`
- ⬆️ Updated `spotdl` from `4.2.4` to `>=4.4.3` (for compatibility)

### Verification

All components tested and verified working:
- ✅ YouTube downloader functionality
- ✅ Spotify downloader functionality
- ✅ Application startup
- ✅ API endpoints
- ✅ No dependency conflicts

### Current Versions

- yt-dlp: 2025.12.08 (latest)
- spotdl: 4.4.3 (latest)

### Recommendation

If you have an existing installation, update dependencies immediately:

```bash
pip install --upgrade -r requirements.txt
```

### References

- [yt-dlp Security Advisory](https://github.com/yt-dlp/yt-dlp/security/advisories)
- [CVE-2023-40581](https://nvd.nist.gov/vuln/detail/CVE-2023-40581)

---

Last updated: January 28, 2026
