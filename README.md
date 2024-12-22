Choosing the right parameters to forecast : 
- Temperature (at 2m)
- Precipitations
- Wind direction (10m, size of a building)
- Wind speed

We will take into account the actual conditions and the forecasted ones. We have access to hourly forecasts. 
If the conditions in the next hour are going to be different from the actual conditions, we can trigger a particular response. 

The chosen coordinates are the ones from our usual building classroom (bat I), even though this one is underground but it is just for the sake of the example. Coordinates : 45.065037, 7.658205
For scalability reasons, we added a FOR loop and a locations dictionnary.

We have 10_000 free queries per day, so during 24h we could easily run a query evry 15 min (the data is uploaded by the API evry 15min either way so we can not do more)

22/12/2024 : still to do
- weather api scalability complete, still need more definition on the exact file format and what we want to be sent
- try to run and create a local host to see if the information goes well from the weather to the adaptor
- dockerize the adaptor, test the sending via local host
- do the Telegram bot
