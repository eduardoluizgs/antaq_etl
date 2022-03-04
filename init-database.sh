for i in {1..50};
do
    /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -d master -i init-database.sql
    if [ $? -eq 0 ]
    then
        echo "init-database.sql executed!"
        break
    else
        echo "Not Ready. Waiting for SQL Server Init..."
        sleep 1
    fi
done
