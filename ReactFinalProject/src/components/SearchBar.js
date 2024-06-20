import React from 'react';
import { Form, FormControl } from 'react-bootstrap';
import './SearchBar.scss';

const SearchBar = ({ setSearchTerm }) => (
    <Form inline className="search-bar">
        <Form.Label>Search</Form.Label>
        <FormControl
            type="text"
            placeholder="Search"
            className="mr-sm-2 filter-input"
            onChange={(e) => setSearchTerm(e.target.value)}
        />
    </Form>
);

export default SearchBar;
