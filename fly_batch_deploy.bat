$entries = Get-Content .\fly_batch_deploy.json -Raw | ConvertFrom-Json
$flyTomlPath = Join-Path (Get-Location) 'fly.toml'
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

foreach ($entry in $entries) {
      $content = [System.IO.File]::ReadAllText($flyTomlPath)

      $content = [System.Text.RegularExpressions.Regex]::Replace(
          $content,
          '^(app\s*=\s*).*$',
          ('$1"' + $entry.app + '"'),
          [System.Text.RegularExpressions.RegexOptions]::Multiline
      )

      $content = [System.Text.RegularExpressions.Regex]::Replace(
          $content,
          '^(primary_region\s*=\s*).*$',
          ('$1"' + $entry.region + '"'),
          [System.Text.RegularExpressions.RegexOptions]::Multiline
      )

      [System.IO.File]::WriteAllText($flyTomlPath, $content, $utf8NoBom)

      Write-Host "Deploying cmd=$($entry.cmd) app=$($entry.app) region=$($entry.region)"
      & $entry.cmd deploy --ha=false -a $entry.app
}