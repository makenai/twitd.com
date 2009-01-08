$(document).ready(function(){
	$('ul.rt-list').hide();
	$('a.toggle-list').click(function () {
		$(this).next('ul.rt-list').toggle('fast');
		return false;
	});
	$('a.counter-toggle').click(function () {
		$(this).nextAll('ul.rt-list').toggle('fast');
		return false;
	});
});
