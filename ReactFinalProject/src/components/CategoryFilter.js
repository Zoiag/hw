import React, { useEffect, useState } from 'react';
import { Form } from 'react-bootstrap';
import './CategoryFilter.scss';

const CategoryFilter = ({ setCategory }) => {
    const [categories, setCategories] = useState([]);

    useEffect(() => {
        fetch('http://openlibrary.org/search.json?q=the+lord+of+the+rings&lang=eng&limit=100')
            .then(response => response.json())
            .then(data => {
                const authors = Array.from(new Set(data.docs.map(book => book.author_name).flat().filter(Boolean)));
                setCategories(authors);
            })
            .catch(error => console.error('Error fetching data:', error));
    }, []);

    return (
        <Form className="category-filter">
            <Form.Group controlId="categorySelect">
                <Form.Label>Author</Form.Label>
                <Form.Control as="select" onChange={(e) => setCategory(e.target.value)} className="filter-input">
                    <option value="">All</option>
                    {categories.map(category => (
                        <option key={category} value={category}>{category}</option>
                    ))}
                </Form.Control>
            </Form.Group>
        </Form>
    );
};

export default CategoryFilter;
