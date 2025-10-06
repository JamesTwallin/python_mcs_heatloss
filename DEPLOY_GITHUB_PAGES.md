# Deploy to GitHub Pages

Quick guide to deploy the 3D Heat Loss Calculator to GitHub Pages.

## Method 1: Quick Deploy (Recommended)

### Step 1: Push to GitHub

```bash
cd C:\Users\User\Documents\GitHub\python_mcs_heatloss

# Add all web files
git add web/
git add DEPLOY_GITHUB_PAGES.md

# Commit
git commit -m "Add 3D heat loss calculator web app"

# Push to GitHub
git push origin main
```

### Step 2: Enable GitHub Pages

1. Go to your repository on GitHub: `https://github.com/YOUR_USERNAME/python_mcs_heatloss`
2. Click **Settings** tab
3. Scroll down to **Pages** section (left sidebar)
4. Under **Source**, select:
   - Branch: `main`
   - Folder: `/ (root)`
5. Click **Save**

### Step 3: Access Your Site

Your site will be available at:
```
https://YOUR_USERNAME.github.io/python_mcs_heatloss/web/
```

GitHub will take 1-2 minutes to build and deploy.

## Method 2: Using gh-pages Branch

### Step 1: Create gh-pages Branch

```bash
# Create and switch to gh-pages branch
git checkout --orphan gh-pages

# Remove all files from staging
git rm -rf .

# Copy web files to root
cp -r web/* .

# Add files
git add .

# Commit
git commit -m "Deploy to GitHub Pages"

# Push
git push origin gh-pages

# Switch back to main
git checkout main
```

### Step 2: Configure GitHub Pages

1. Go to **Settings** → **Pages**
2. Select branch: `gh-pages`
3. Folder: `/ (root)`
4. Save

Site will be at: `https://YOUR_USERNAME.github.io/python_mcs_heatloss/`

## Method 3: GitHub Actions (Automatic)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./web
```

This auto-deploys on every push to main.

## Verification

### Check Deployment Status
1. Go to **Actions** tab on GitHub
2. Look for green checkmark ✅
3. Click on workflow run for details

### Test Your Site
1. Visit your GitHub Pages URL
2. Should see the 3D Heat Loss Calculator
3. Try adding a room to test 3D view

## Troubleshooting

### Site Not Loading
- Wait 2-3 minutes after enabling Pages
- Check **Actions** tab for build errors
- Verify branch and folder settings

### 404 Error
- Make sure files are in correct location
- Check that `index.html` exists in web folder
- Verify GitHub Pages is enabled

### Three.js Not Loading
- Check browser console (F12) for errors
- Verify CDN URLs are accessible
- Try clearing browser cache

### Blank Page
- Open browser console (F12)
- Look for JavaScript errors
- Check that all files were pushed to GitHub

## Custom Domain (Optional)

### Step 1: Add CNAME File

Create `web/CNAME`:
```
heatloss.yourdomain.com
```

### Step 2: Configure DNS

Add DNS records at your domain provider:
```
Type: CNAME
Name: heatloss
Value: YOUR_USERNAME.github.io
```

### Step 3: Enable HTTPS

1. Go to **Settings** → **Pages**
2. Check "Enforce HTTPS"
3. Wait for certificate provisioning (~24 hours)

## Testing Locally Before Deploy

### Python Server
```bash
cd web
python -m http.server 8000
```
Visit: `http://localhost:8000`

### Node.js Server
```bash
cd web
npx http-server
```

### VS Code Live Server
1. Install "Live Server" extension
2. Right-click `index.html`
3. Select "Open with Live Server"

## Updating Your Site

```bash
# Make changes to files in web/

# Add and commit
git add web/
git commit -m "Update 3D calculator"

# Push
git push origin main

# GitHub Pages will auto-update in 1-2 minutes
```

## File Structure for GitHub Pages

```
python_mcs_heatloss/
├── web/
│   ├── index.html          ← Main entry point
│   ├── styles.css          ← Styling
│   ├── app3d.js            ← 3D application
│   ├── README.md           ← Documentation
│   └── test.html           ← Three.js test
├── mcs_calculator/         ← Python code (not deployed)
├── tests/                  ← Tests (not deployed)
└── README.md              ← Main docs (not deployed)
```

Only files in `web/` are needed for GitHub Pages.

## Security Notes

- No server-side code required
- All calculations run client-side
- No data sent to servers
- JSON files stay on user's computer

## Performance

- **First load**: ~1-2 seconds (Three.js download)
- **Subsequent loads**: Instant (cached)
- **3D rendering**: 60 FPS on modern browsers
- **Calculation**: <100ms for typical buildings

## Browser Requirements

Minimum versions:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Requirements:
- WebGL support
- JavaScript enabled
- 1024x768 minimum resolution

## Analytics (Optional)

Add Google Analytics to track usage:

```html
<!-- In index.html <head> -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## Support

If deployment fails:
1. Check GitHub Actions logs
2. Verify all files committed
3. Test locally first
4. Check GitHub Pages documentation

## Next Steps

After deployment:
1. Test all features online
2. Share URL with users
3. Add link to main README
4. Create example JSON files
5. Write user documentation

---

**Quick Command Summary:**
```bash
# Deploy to GitHub Pages
git add web/
git commit -m "Deploy 3D calculator"
git push origin main

# Enable in: Settings → Pages → main branch
# Visit: https://USERNAME.github.io/python_mcs_heatloss/web/
```
