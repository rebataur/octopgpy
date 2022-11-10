  With sma as (
            SELECT     
            trade_date,
            close,
            AVG(close) OVER(ORDER BY trade_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS sma20,
 			AVG(close) OVER(ORDER BY trade_date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) AS sma50,
            AVG(close) OVER(ORDER BY trade_date ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) AS sma200
            
            FROM bse 
            where code = 539448
           ),
    delta as(
    		select *,
    		lead(sma200,1,0) over (order by trade_date) as next_sma200,
            lead(sma50,1,0) over (order by trade_date) as next_sma50,
            lag(sma50,1,0) over (order by trade_date) as prev_sma50,
    		from sma 
    ),
    rising as (
    select *,
    case 
    	when ROUND(next_sma200) - ROUND(sma200) > 0 then TRUE
        else FALSE
    end is_sma200_rising,
        case 
    	when prev_sma50 < sma200 and next_sma50 > sma200 then TRUE
        else FALSE
    end goldencross 
   from delta
   ),
   top5 as (
   	select * from rising  order by trade_date desc limit 1,5
   )     select 
   case when count(*) == 5 then true 
   	else FALSE
   end ok 
   from top5 where is_sma20_rising = true and goldencross = true