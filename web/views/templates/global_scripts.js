/* The JS below is included globally (unless a page over-rides it) */

function _default_ajax_success(data)
{
	return true;
}

function _default_ajax_error(data, error_string)
{
	alertHTML = "<div class=\"alert alert-error\">Error processing AJAX request! Error: \"" + error_string + "\"</div>";
	$('body').prepend(alertHTML);

	return true;
}

function server_post(url, data, success_function, error_function)
{
	/* Push data to the server using AJAX.
	 * This function returns immediately */
	
	if (typeof(url) !== "string")
		return false;

	if (typeof(data) !== "object")
		return false;

	if (typeof(success_function) !== "function")
		success_function = _default_ajax_success;

	if (typeof(error_function) !== "function")
		error_function = _default_ajax_error;

	return 
		jQuery.ajax({
			type: "POST",
			url:  url,
			data: data,
			success: success_function,
			error: error_function
		});
}

function sserver_post(url, data, success_function, error_function)
{
	/* Push data to the server using AJAX, and do so synchronously.
	 * That is, this function won't return until the request completes.*/
	if (typeof(url) !== "string")
		return false;

	if (typeof(data) !== "object")
		return false;

	if (typeof(success_function) !== "function")
		success_function = _default_ajax_success;

	if (typeof(error_function) !== "function")
		error_function = _default_ajax_error;

	return
		jQuery.ajax({
			type: "POST",
			url: url,
			data: data,
			success: success_function,
			error: error_function,
			async: false
		});
}
