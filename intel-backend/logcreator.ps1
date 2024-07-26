# Define variables for the log entry
$source = "MyApplication"
$logName = "Application"
$eventId = 1001
$entryType = "Information"
$message = "This is a test log entry."

# Check if the event log source exists; if not, create it
if (-not (Get-EventLog -List | Where-Object { $_.Log -eq $logName })) {
    New-EventLog -LogName $logName -Source $source
}

# Write the event log entry
Write-EventLog -LogName $logName -Source $source -EventId $eventId -EntryType $entryType -Message $message

# Output confirmation message
Write-Host "Log entry created successfully."
