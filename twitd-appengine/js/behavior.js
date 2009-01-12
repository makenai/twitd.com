$(document).ready(function(){
	$('ul.rt-list').hide();
	$('a.counter-toggle').click(function () {
		var rt_list = $(this).nextAll('ul.rt-list');
		if ( rt_list.children('li').hasClass('default') ) {
			var tweet_id = rt_list.parents('div.thread').attr('id').split('-')[1];
			rt_list.load("/retweets/" + tweet_id, null, function( ){
				rt_list.toggle('fast');
			});
		} else {
			rt_list.toggle('fast');
		}
		return false;
	});
});
