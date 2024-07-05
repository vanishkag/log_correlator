# Save this as ExportSystemLogs.ps1

# Define the path to save the CSV file
$csvPath = "C:\Users\nanda\Documents\intel\log_correlator\SystemLog.csv"
# Export System logs to CSV
Get-WinEvent -LogName System -MaxEvents 200 | Select-Object -Property TimeCreated, Id, LevelDisplayName, Message | Export-Csv -Path $csvPath -NoTypeInformation

# Export Application logs to CSV
$csvPathApp = "C:\Users\nanda\Documents\intel\log_correlator\ApplicationLog.csv"
Get-WinEvent -LogName Application -MaxEvents 200 | Select-Object -Property TimeCreated, Id, LevelDisplayName, Message | Export-Csv -Path $csvPathApp -NoTypeInformation

# Export Security logs to CSV (requires admin privileges)
$csvPathSec = "C:\Users\nanda\Documents\intel\log_correlator\SecurityLog.csv"
Get-WinEvent -LogName Security -MaxEvents 200 | Select-Object -Property TimeCreated, Id, LevelDisplayName, Message | Export-Csv -Path $csvPathSec -NoTypeInformation
