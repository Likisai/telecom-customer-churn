$ErrorActionPreference = "Stop"

$files = @(
    "Anaganti_Sairishikesh.docx",
    "TelcoPulse_AI_GenAI_LB1_Project_Report_Anaganti_Sairishikesh.docx",
    "Telecom_Customer_Churn_Project_Report_Anaganti_Sairishikesh.docx"
)

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.ScreenUpdating = $false
    $word.DisplayAlerts = 0 # wdAlertsNone

    foreach ($f in $files) {
        $inDoc = Join-Path (Get-Location) $f
        $outPdf = Join-Path (Get-Location) ($f -replace '\.docx$', '.pdf')
        
        Write-Host "Processing: $inDoc"
        $doc = $word.Documents.Open($inDoc, $false, $true, $false)
        # 17 = wdExportFormatPDF
        $doc.ExportAsFixedFormat($outPdf, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
        $doc.Close([ref]0)
        Write-Host "Created: $outPdf (Size: $((Get-Item $outPdf).Length) bytes)"
    }
}
catch {
    Write-Error $_.Exception.Message
}
finally {
    if ($word) {
        $word.Quit([ref]0)
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
    }
}
