/*
	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

function detectTab(text) {
	/*
		Tries to deduce if it's a tab (\t) or soft tabs (spaces)
		and if it's a soft tab how many tabs. The function works
		on a passed in value of text which should be an string or
		array of a section of source code. If no tab scheme is found
		or a mixed scheme is found a tab of 4 spaces will be returned.

		This will return the tab (e.g. '\t' or '    ')
	*/

	if (typeof text === 'string') {
		// we always want to be dealing with an array.
		text = [text];
	}

	return '    '; // Do somethin smart
}

function detectLanguage(code) {
	/*
		Will attempt to peform a language detection, will return null
		if couldn't detect or a string of the language detected.
	*/

	// this should only contain special cases
	var shabangMap = {
		'node': 'js'
	};

	var intepreter;
	if (code.substring(0, 14) == ('#!/usr/bin/env')) {
		// They've started this with a enviroment, parse out intepreter
		var shabang = code.replace('\r', '').split('\n')[0];
		intepreter = shabang.split(' ')[1];
	} else if (code.substring(0, 2) == ('#!')) {
		// Normal shabang (we hope)
		var parts = code.split('\n')[0].split('/');
		intepreter = parts[parts.length - 1].replace('\r', '').split(' ')[0];
	}

	if (intepreter !== undefined) {
		var languageField = document.getElementById('id_language');

		for(var i = 0; i < languageField.options.length; i++) {
			// why doesn't .forEach work :(
			var language = languageField.options[i].value;
			if (intepreter == language) {
				return language;
			}
		}

		if (shabangMap[intepreter] !== undefined) {
			return shabangMap[intepreter];
		}
	}

	return null; // Awh.


}

// Once the DOM has loaded we need some code to be called
window.onload = function () {
	var contentElement = document.getElementById('id_content');
	if (!contentElement) {
		return;
	}

	// On load focus the pastebin area
	contentElement.focus();

	var tabType;

	contentElement.onkeydown = function (key) {
		/*
			This function takes in a key press from the paste content
			area and relays this into the desired action:
				e.g.
					tab -> insert tab
		*/

		var startPosition = this.selectionStart;
		var endPosition = this.selectionEnd;
		var line = this.value;

		if (tabType === undefined && (key.keyCode == 13 || key.keyCode == 9 || key.keyCode == 8)) {
			// Detect tab if we haven't already and we need to (backspace or tab).
			tabType = detectTab(document.value);
		}

		if (key.keyCode == 9) {
			// Tab pressed.
			var lineFragment = line.substring(0, startPosition);
			var fragments = [
				lineFragment,
				tabType,
				line.substring(endPosition)
			];

			var cursorPosition = lineFragment.length+tabType.length;

			this.value = fragments.join('');
			contentElement.setSelectionRange(cursorPosition, cursorPosition);
			return false; // Don't tab away from element.

		}

		if (key.keyCode == 8) {
			// Backspace - if it's a tab, remove ALL of them
			var lineFragment = line.substring(0, startPosition);
			var remainder = line.substring(endPosition);
			var tabSpace = lineFragment.substring(lineFragment.length-tabType.length, lineFragment.length);

			var newCursor;
			if (tabType == tabSpace) {
				newCursor = lineFragment.length-tabType.length;
				this.value = lineFragment.substring(0, newCursor);
				this.value += remainder;

				var windowScrollTop = window.scrollTop;
				var scrollTop = contentElement.scrollTop;
				// Set the cursor where it's meant to be (behind recetly removed tab)
				contentElement.setSelectionRange(newCursor, newCursor);

				// setSelectionRange can cause scrolling, don't.
				contentElement.scrollTop = scrollTop;
				window.scrollTop = windowScrollTop;
				return false; // don't do anything, I have.
			} else {
				return true;
			}
		}

		if (key.keyCode == 13) {
			// Enter/Carrage return
			var languageField = document.getElementById('id_language');
			var language = detectLanguage(contentElement.value);
			if (language && languageField.value === 'None') {
				languageField.value = language;
			}
		}
	}
}