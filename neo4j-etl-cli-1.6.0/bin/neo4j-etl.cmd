@echo off
set jarpath=%0
set jarpath=%jarpath:\neo4j-etl=%\..
setlocal enabledelayedexpansion
	set jars=
    for /f "delims=" %%a in ('dir %jarpath%\lib\*.jar /s/b') do set jars=%%a;!jars!
	set jars=!jars:~0,-1!
	echo %jars%
endlocal & java -classpath %jars% org.neo4j.etl.NeoIntegrationCli %*