A script to incrementally parse and back up SL logs to a MySQL database.
Set up your database, edit and apply sllog.sql, edit your .init,
then run the script from cron / task scheduler.
The first import can take a long time for long logs, but updates are fast.
