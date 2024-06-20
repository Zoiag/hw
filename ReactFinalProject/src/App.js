import React, { useEffect, useState } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import CategoryFilter from './components/CategoryFilter';
import YearFilter from './components/YearFilter'; // Новый компонент
import ItemList from './components/ItemList';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.scss';

const App = () => {
    const [books, setBooks] = useState([]);
    const [filteredBooks, setFilteredBooks] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [category, setCategory] = useState('');
    const [year, setYear] = useState('');

    useEffect(() => {
        fetch('http://openlibrary.org/search.json?q=the+lord+of+the+rings&lang=eng&limit=200')
            .then(response => response.json())
            .then(data => {
                const booksWithImages = data.docs.filter(book => book.cover_i);
                setBooks(booksWithImages);
                setFilteredBooks(booksWithImages);
            })
            .catch(error => console.error('Error fetching data:', error));
    }, []);

    useEffect(() => {
        let tempBooks = books;
        if (searchTerm) {
            tempBooks = tempBooks.filter(book => book.title.toLowerCase().includes(searchTerm.toLowerCase()));
        }
        if (category) {
            tempBooks = tempBooks.filter(book => book.author_name && book.author_name.includes(category));
        }
        if (year) {
            tempBooks = tempBooks.filter(book => book.first_publish_year && book.first_publish_year === parseInt(year));
        }
        setFilteredBooks(tempBooks);
    }, [searchTerm, category, year, books]);

    return (
        <div className="App">
            <Header />
            <div className="filters">
                <SearchBar setSearchTerm={setSearchTerm} />
                <CategoryFilter setCategory={setCategory} />
                <YearFilter setYear={setYear} /> {/* Новый компонент */}
            </div>
            <ItemList items={filteredBooks} />
        </div>
    );
};

export default App;
